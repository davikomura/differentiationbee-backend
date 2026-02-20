from collections import Counter
from threading import Lock


_LOCK = Lock()
_REQUESTS = Counter()
_STATUS = Counter()


def record_request(path: str, method: str, status_code: int) -> None:
    with _LOCK:
        _REQUESTS[f"{method} {path}"] += 1
        _STATUS[str(status_code)] += 1


def metrics_snapshot() -> dict:
    with _LOCK:
        return {
            "requests_by_route": dict(_REQUESTS),
            "responses_by_status": dict(_STATUS),
        }
