from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _normalize_detail(detail: Any) -> tuple[str, Any]:
    if isinstance(detail, str):
        return detail, None
    if isinstance(detail, dict):
        message = str(detail.get("message") or detail.get("detail") or "Request failed")
        return message, detail
    if isinstance(detail, list):
        return "Request failed", detail
    return "Request failed", {"detail": detail}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        message, details = _normalize_detail(exc.detail)
        payload: dict[str, Any] = {
            "ok": False,
            "error": {
                "code": f"http_{exc.status_code}",
                "message": message,
            },
            "path": request.url.path,
        }
        if details is not None:
            payload["error"]["details"] = details
        return JSONResponse(status_code=exc.status_code, content=payload, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request payload or parameters",
                    "details": exc.errors(),
                },
                "path": request.url.path,
            },
        )
