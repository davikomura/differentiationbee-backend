import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} nao configurada")
    return value.strip()


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} deve ser inteiro") from exc


def _parse_origins(value: str | None) -> list[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",")]
    return [p for p in parts if p]


class Settings:
    def __init__(self) -> None:
        self.database_url = _get_required_env("DATABASE_URL")
        self.jwt_secret_key = _get_required_env("JWT_SECRET_KEY")

        self.access_token_expire_minutes = _get_int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
        self.refresh_token_expire_days = _get_int_env("REFRESH_TOKEN_EXPIRE_DAYS", 30)
        self.max_refresh_tokens_per_user = _get_int_env("MAX_REFRESH_TOKENS_PER_USER", 3)

        self.cors_allow_origins = _parse_origins(os.getenv("CORS_ALLOW_ORIGINS")) or ["http://localhost:5173"]

        self.rate_limit_requests = _get_int_env("RATE_LIMIT_REQUESTS", 120)
        self.rate_limit_window_seconds = _get_int_env("RATE_LIMIT_WINDOW_SECONDS", 60)


@lru_cache
def get_settings() -> Settings:
    return Settings()
