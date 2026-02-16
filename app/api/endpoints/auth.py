# app/api/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from app.db.session import get_db
from app.schemas.auth import UserCreate, UserLogin, UserRead, TokenPair, RefreshRequest, LogoutRequest
from app.services.auth import register_user, authenticate_user, create_tokens_for_user
from app.core.security import decode_access_token, create_access_token
from app.models.user import User
from app.models.user_stats import UserStats
from app.services.elo import get_arena_for_rating, arena_progress
from app.services.refresh_tokens import rotate_refresh_token, revoke_refresh_token
from app.core.ratelimit import enforce_rate_limit, RateLimit

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)

@router.post("/login", response_model=TokenPair)
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    enforce_rate_limit(request, "auth_login", RateLimit(limit=8, window_seconds=60))
    user = authenticate_user(db, login_data)
    return create_tokens_for_user(db, user)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sem subject (sub)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(sub)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (sub não é inteiro)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/refresh")
def refresh(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)):
    enforce_rate_limit(request, "auth_refresh", RateLimit(limit=20, window_seconds=60))
    user_id = rotate_refresh_token(db, payload.refresh_token)
    access = create_access_token(subject=str(user_id))
    return {"access_token": access, "token_type": "bearer"}

@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    revoke_refresh_token(db, payload.refresh_token)
    return {"message": "Logout realizado"}

@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()
    rating = int(stats.rating) if stats else 100
    arena = get_arena_for_rating(rating)
    prog = arena_progress(rating, arena)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat(),
        "elo": {
            "rating": rating,
            "arena": {
                "index": arena.index,
                "name": arena.name,
                "min_rating": prog["min"],
                "max_rating": prog["max"],
                "progress": prog["pct"],
            },
        },
    }