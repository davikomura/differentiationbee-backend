from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.metrics import metrics_snapshot


router = APIRouter()


@router.get("/healthz")
def healthz():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/metrics")
def metrics():
    return metrics_snapshot()
