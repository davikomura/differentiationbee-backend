from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Any

from app.core.settings import get_settings

try:
    import redis
except Exception:  # pragma: no cover - optional dependency for local dev
    redis = None


class RateLimitStore:
    def is_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        raise NotImplementedError


class InMemoryRateLimitStore(RateLimitStore):
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def is_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now = time.time()
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - window_seconds
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= max_requests:
                return True

            bucket.append(now)
            return False


class RedisRateLimitStore(RateLimitStore):
    def __init__(self, redis_url: str) -> None:
        if redis is None:
            raise RuntimeError("STATE_BACKEND=redis requer dependencia 'redis' instalada")
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def is_limited(self, key: str, max_requests: int, window_seconds: int) -> bool:
        now_ms = int(time.time() * 1000)
        cutoff_ms = now_ms - (window_seconds * 1000)
        redis_key = f"dbee:ratelimit:{key}"
        member = f"{now_ms}:{time.time_ns()}"

        pipe = self._client.pipeline()
        pipe.zremrangebyscore(redis_key, 0, cutoff_ms)
        pipe.zadd(redis_key, {member: now_ms})
        pipe.zcard(redis_key)
        pipe.expire(redis_key, max(1, window_seconds))
        _, _, count, _ = pipe.execute()
        return int(count) > int(max_requests)


class CompetitiveStore:
    def pop_pending(self, user_id: int) -> dict | None:
        raise NotImplementedError

    def is_user_in_queue(self, user_id: int) -> bool:
        raise NotImplementedError

    def find_and_pop_opponent(self, rating: int, level: int, tolerance: int, exclude_user_id: int) -> dict | None:
        raise NotImplementedError

    def enqueue(self, entry: dict) -> None:
        raise NotImplementedError

    def bind_match(self, session_a_id: int, session_b_id: int, payload: dict) -> None:
        raise NotImplementedError

    def get_match(self, session_id: int) -> dict | None:
        raise NotImplementedError

    def set_pending(self, user_id: int, payload: dict) -> None:
        raise NotImplementedError

    def mark_match_rated(self, match_id: str) -> bool:
        raise NotImplementedError


class InMemoryCompetitiveStore(CompetitiveStore):
    def __init__(self) -> None:
        self._queue: deque[dict] = deque()
        self._pending_by_user: dict[int, dict] = {}
        self._match_by_session: dict[int, dict] = {}
        self._rated_matches: set[str] = set()
        self._lock = Lock()

    def pop_pending(self, user_id: int) -> dict | None:
        with self._lock:
            return self._pending_by_user.pop(int(user_id), None)

    def is_user_in_queue(self, user_id: int) -> bool:
        with self._lock:
            return any(int(x["user_id"]) == int(user_id) for x in self._queue)

    def find_and_pop_opponent(self, rating: int, level: int, tolerance: int, exclude_user_id: int) -> dict | None:
        with self._lock:
            opponent_idx: int | None = None
            for idx, entry in enumerate(self._queue):
                if int(entry["user_id"]) == int(exclude_user_id):
                    continue
                if int(entry["level"]) != int(level):
                    continue
                if abs(int(entry["rating"]) - int(rating)) <= int(tolerance):
                    opponent_idx = idx
                    break

            if opponent_idx is None:
                return None

            opponent = self._queue[opponent_idx]
            del self._queue[opponent_idx]
            return dict(opponent)

    def enqueue(self, entry: dict) -> None:
        with self._lock:
            self._queue.append(dict(entry))

    def bind_match(self, session_a_id: int, session_b_id: int, payload: dict) -> None:
        with self._lock:
            self._match_by_session[int(session_a_id)] = dict(payload)
            self._match_by_session[int(session_b_id)] = dict(payload)

    def get_match(self, session_id: int) -> dict | None:
        with self._lock:
            payload = self._match_by_session.get(int(session_id))
            return dict(payload) if payload else None

    def set_pending(self, user_id: int, payload: dict) -> None:
        with self._lock:
            self._pending_by_user[int(user_id)] = dict(payload)

    def mark_match_rated(self, match_id: str) -> bool:
        with self._lock:
            if match_id in self._rated_matches:
                return False
            self._rated_matches.add(match_id)
            return True


class RedisCompetitiveStore(CompetitiveStore):
    QUEUE_USERS_KEY = "dbee:ranked:queued_users"
    PENDING_HASH_KEY = "dbee:ranked:pending_by_user"
    MATCH_HASH_KEY = "dbee:ranked:match_by_session"

    def __init__(self, redis_url: str) -> None:
        if redis is None:
            raise RuntimeError("STATE_BACKEND=redis requer dependencia 'redis' instalada")
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)

    def _queue_key(self, level: int) -> str:
        return f"dbee:ranked:queue:level:{int(level)}"

    def _with_lock(self, lock_name: str, fn):
        lock = self._client.lock(lock_name, timeout=5, blocking_timeout=2)
        if not lock.acquire(blocking=True):
            raise RuntimeError("Nao foi possivel adquirir lock do estado ranked")
        try:
            return fn()
        finally:
            try:
                lock.release()
            except Exception:
                pass

    def pop_pending(self, user_id: int) -> dict | None:
        raw = self._client.hget(self.PENDING_HASH_KEY, str(int(user_id)))
        if not raw:
            return None
        self._client.hdel(self.PENDING_HASH_KEY, str(int(user_id)))
        return json.loads(raw)

    def is_user_in_queue(self, user_id: int) -> bool:
        return bool(self._client.sismember(self.QUEUE_USERS_KEY, str(int(user_id))))

    def find_and_pop_opponent(self, rating: int, level: int, tolerance: int, exclude_user_id: int) -> dict | None:
        queue_key = self._queue_key(level)

        def _run():
            rows = self._client.lrange(queue_key, 0, -1)
            for raw in rows:
                entry = json.loads(raw)
                if int(entry.get("user_id", 0)) == int(exclude_user_id):
                    continue
                if int(entry.get("level", 0)) != int(level):
                    continue
                if abs(int(entry.get("rating", 0)) - int(rating)) > int(tolerance):
                    continue
                self._client.lrem(queue_key, 1, raw)
                self._client.srem(self.QUEUE_USERS_KEY, str(int(entry["user_id"])))
                return entry
            return None

        return self._with_lock("dbee:ranked:queue:lock", _run)

    def enqueue(self, entry: dict) -> None:
        queue_key = self._queue_key(int(entry["level"]))
        payload = json.dumps(entry, separators=(",", ":"), ensure_ascii=False)

        def _run():
            self._client.rpush(queue_key, payload)
            self._client.sadd(self.QUEUE_USERS_KEY, str(int(entry["user_id"])))
            self._client.expire(queue_key, 3600)
            self._client.expire(self.QUEUE_USERS_KEY, 3600)

        self._with_lock("dbee:ranked:queue:lock", _run)

    def bind_match(self, session_a_id: int, session_b_id: int, payload: dict) -> None:
        raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        pipe = self._client.pipeline()
        pipe.hset(self.MATCH_HASH_KEY, str(int(session_a_id)), raw)
        pipe.hset(self.MATCH_HASH_KEY, str(int(session_b_id)), raw)
        pipe.expire(self.MATCH_HASH_KEY, 24 * 3600)
        pipe.execute()

    def get_match(self, session_id: int) -> dict | None:
        raw = self._client.hget(self.MATCH_HASH_KEY, str(int(session_id)))
        if not raw:
            return None
        return json.loads(raw)

    def set_pending(self, user_id: int, payload: dict) -> None:
        self._client.hset(self.PENDING_HASH_KEY, str(int(user_id)), json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
        self._client.expire(self.PENDING_HASH_KEY, 3600)

    def mark_match_rated(self, match_id: str) -> bool:
        rated_key = f"dbee:ranked:rated:{match_id}"
        created = self._client.set(rated_key, "1", ex=7 * 24 * 3600, nx=True)
        return bool(created)


_rate_limit_store: RateLimitStore | None = None
_competitive_store: CompetitiveStore | None = None
_store_lock = Lock()


def get_rate_limit_store() -> RateLimitStore:
    global _rate_limit_store
    if _rate_limit_store is not None:
        return _rate_limit_store

    settings = get_settings()
    with _store_lock:
        if _rate_limit_store is not None:
            return _rate_limit_store
        if settings.state_backend == "redis":
            if not settings.redis_url:
                raise RuntimeError("STATE_BACKEND=redis exige REDIS_URL configurada")
            _rate_limit_store = RedisRateLimitStore(settings.redis_url)
        else:
            _rate_limit_store = InMemoryRateLimitStore()
        return _rate_limit_store


def get_competitive_store() -> CompetitiveStore:
    global _competitive_store
    if _competitive_store is not None:
        return _competitive_store

    settings = get_settings()
    with _store_lock:
        if _competitive_store is not None:
            return _competitive_store
        if settings.state_backend == "redis":
            if not settings.redis_url:
                raise RuntimeError("STATE_BACKEND=redis exige REDIS_URL configurada")
            _competitive_store = RedisCompetitiveStore(settings.redis_url)
        else:
            _competitive_store = InMemoryCompetitiveStore()
        return _competitive_store
