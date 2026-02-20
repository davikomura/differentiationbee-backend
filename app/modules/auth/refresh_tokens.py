from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.i18n import t
from app.core.settings import get_settings
from app.modules.auth.models import RefreshToken

settings = get_settings()

REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days
MAX_REFRESH_TOKENS_PER_USER = settings.max_refresh_tokens_per_user


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cleanup_old_tokens_for_user(db: Session, user_id: int) -> None:
    if MAX_REFRESH_TOKENS_PER_USER <= 0:
        return

    q = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id)
        .order_by(RefreshToken.created_at.desc())
    )

    tokens = q.all()
    if len(tokens) <= MAX_REFRESH_TOKENS_PER_USER:
        return

    to_delete = tokens[MAX_REFRESH_TOKENS_PER_USER:]
    for token in to_delete:
        db.delete(token)

    db.commit()


def issue_refresh_token(db: Session, user_id: int, cleanup: bool = True) -> str:
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires,
            revoked=False,
        )
    )
    db.commit()

    if cleanup:
        _cleanup_old_tokens_for_user(db, user_id)

    return raw


def revoke_all_refresh_tokens_for_user(db: Session, user_id: int) -> int:
    count = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False)  # noqa: E712
        .update({"revoked": True}, synchronize_session=False)
    )
    db.commit()
    return int(count or 0)


def issue_refresh_token_for_login(db: Session, user_id: int) -> str:
    revoke_all_refresh_tokens_for_user(db, user_id)
    return issue_refresh_token(db, user_id, cleanup=True)


def rotate_refresh_token(db: Session, raw_token: str, locale: str = "en") -> tuple[int, str]:
    token_hash = _hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if not rt or rt.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("refresh_invalid", locale))

    now = datetime.now(timezone.utc)
    if rt.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("refresh_expired", locale))

    rt.revoked = True
    db.commit()

    new_raw = issue_refresh_token(db, rt.user_id, cleanup=True)
    return int(rt.user_id), new_raw


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token_hash = _hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if rt:
        rt.revoked = True
        db.commit()
