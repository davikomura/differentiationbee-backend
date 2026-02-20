from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.i18n import get_request_locale, t
from app.core.security import create_access_token, decode_access_token
from app.db.session import get_db
from app.modules.auth.refresh_tokens import revoke_refresh_token, rotate_refresh_token
from app.modules.auth.schemas import LogoutRequest, RefreshRequest, TokenPair, UserCreate, UserLogin, UserRead
from app.modules.auth.service import authenticate_user, create_tokens_for_user, register_user
from app.modules.tiers.service import get_tier_for_points, tier_to_read
from app.modules.users.models import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserRead)
def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    return register_user(db, user, locale=get_request_locale(request))


@router.post("/login", response_model=TokenPair)
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    locale = get_request_locale(request)
    user = authenticate_user(db, login_data, locale=locale)
    return create_tokens_for_user(db, user)


def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    locale = get_request_locale(request)
    payload = decode_access_token(token, locale=locale)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("token_missing_sub", locale),
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(sub)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("token_invalid_sub", locale),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("token_user_not_found", locale),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    user_id, new_refresh = rotate_refresh_token(db, payload.refresh_token, locale=get_request_locale(request))
    access = create_access_token(subject=str(user_id))
    return TokenPair(access_token=access, refresh_token=new_refresh)


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    revoke_refresh_token(db, payload.refresh_token)
    return {"message": "Logout realizado"}


@router.get("/me")
def me(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    locale = get_request_locale(request)

    points = int(getattr(current_user, "points", 0))
    tier = tier_to_read(get_tier_for_points(db, points), locale)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": getattr(current_user, "role", "user"),
        "points": points,
        "tier": tier,
        "created_at": current_user.created_at.isoformat(),
    }
