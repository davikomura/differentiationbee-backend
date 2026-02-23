import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.metrics import record_request
from app.core.state_backends import get_rate_limit_store


logger = logging.getLogger("differentiationbee.api")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - started) * 1000)

        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        record_request(request.url.path, request.method, response.status_code)
        return response


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window_seconds: int):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store = get_rate_limit_store()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/healthz", "/docs", "/openapi.json", "/redoc"}:
            return await call_next(request)

        key = request.client.host if request.client else "unknown"
        if self._store.is_limited(key, self.max_requests, self.window_seconds):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit excedido. Tente novamente em instantes."},
            )

        return await call_next(request)
