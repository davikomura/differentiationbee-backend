# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",")]
    return [p for p in parts if p]

app = FastAPI(
    title="Differentiation Bee",
    version="1.2.0",
)

origins = _parse_origins(os.getenv("CORS_ALLOW_ORIGINS")) or ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)