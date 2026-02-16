# app/services/refresh_tokens.py
from __future__ import annotations
import os
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.refresh_token import RefreshToken

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or "30")

def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def issue_refresh_token(db: Session, user_id: int) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires, revoked=False))
    db.commit()
    return raw

def rotate_refresh_token(db: Session, raw_token: str) -> int:
    token_hash = _hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not rt or rt.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    now = datetime.now(timezone.utc)
    if rt.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expirado")

    rt.revoked = True
    db.commit()
    return int(rt.user_id)

def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token_hash = _hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if rt:
        rt.revoked = True
        db.commit()