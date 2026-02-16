# app/core/ratelimit.py
from __future__ import annotations
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Tuple
from fastapi import HTTPException, Request

@dataclass(frozen=True)
class RateLimit:
    limit: int
    window_seconds: int

_BUCKETS: Dict[Tuple[str, str], Deque[float]] = {}

def _now() -> float:
    return time.time()

def enforce_rate_limit(request: Request, key: str, rule: RateLimit) -> None:
    ip = request.client.host if request.client else "unknown"
    bucket_key = (ip, key)
    q = _BUCKETS.get(bucket_key)
    if q is None:
        q = deque()
        _BUCKETS[bucket_key] = q

    now = _now()
    cutoff = now - rule.window_seconds
    while q and q[0] < cutoff:
        q.popleft()

    if len(q) >= rule.limit:
        raise HTTPException(status_code=429, detail="Muitas requisições. Tente novamente em instantes.")

    q.append(now)