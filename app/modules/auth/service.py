# app/modules/auth/service.py
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.modules.users.models import User
from app.modules.auth.schemas import UserCreate, UserLogin, TokenPair
from app.core.security import create_access_token
from app.modules.auth.refresh_tokens import issue_refresh_token_for_login
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str):
    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Senha fraca. Use ao menos 8 caracteres, uma letra maiúscula e um número.",
        )

def register_user(db: Session, user_data: UserCreate):
    user_data.username = user_data.username.strip().lower()
    user_data.email = user_data.email.strip().lower()

    if not re.match(r"^[a-z0-9_.-]+$", user_data.username):
        raise HTTPException(
            status_code=400,
            detail="Nome de usuário inválido. Use apenas letras minúsculas, números, '.', '-' ou '_'",
        )

    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Usuário ou email já em uso.")

    validate_password_strength(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def authenticate_user(db: Session, login_data: UserLogin):
    username = login_data.username.strip().lower()

    user = db.query(User).filter(User.username == username).first()
    hashed = user.hashed_password if user else os.getenv("DUMMY_BCRYPT_HASH")
    pwd_ok = verify_password(login_data.password, hashed)

    if not user or not pwd_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def create_tokens_for_user(db: Session, user: User) -> TokenPair:
    access = create_access_token(subject=str(user.id))

    refresh = issue_refresh_token_for_login(db, user.id)

    return TokenPair(access_token=access, refresh_token=refresh)