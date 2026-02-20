import os
import re

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.i18n import t
from app.core.security import create_access_token
from app.modules.auth.refresh_tokens import issue_refresh_token_for_login
from app.modules.auth.schemas import TokenPair, UserCreate, UserLogin
from app.modules.users.models import User
from app.modules.users.roles import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DUMMY_HASH_FALLBACK = "$2b$12$C6UzMDM.H6dfI/f/IKcEeO8d2Z7m6bFZl1b0xj5c5q9t0G9q9bJrS"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_strength(password: str, locale: str = "en"):
    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail=t("password_weak", locale))


def register_user(db: Session, user_data: UserCreate, locale: str = "en"):
    user_data.username = user_data.username.strip().lower()
    user_data.email = user_data.email.strip().lower()

    if not re.match(r"^[a-z0-9_.-]+$", user_data.username):
        raise HTTPException(status_code=400, detail=t("username_invalid", locale))

    existing = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail=t("user_or_email_in_use", locale))

    validate_password_strength(user_data.password, locale)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=UserRole.user.value,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(db: Session, login_data: UserLogin, locale: str = "en"):
    username = login_data.username.strip().lower()

    user = db.query(User).filter(User.username == username).first()
    hashed = user.hashed_password if user else (os.getenv("DUMMY_BCRYPT_HASH") or DUMMY_HASH_FALLBACK)
    pwd_ok = verify_password(login_data.password, hashed)

    if not user or not pwd_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("credentials_invalid", locale),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_tokens_for_user(db: Session, user: User) -> TokenPair:
    access = create_access_token(subject=str(user.id))
    refresh = issue_refresh_token_for_login(db, user.id)
    return TokenPair(access_token=access, refresh_token=refresh)
