# app/modules/seasons/router.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.permissions import require_roles
from app.modules.seasons.schemas import SeasonCreate, SeasonRead
from app.modules.seasons.service import create_season, get_active_season_localized
from app.modules.users.models import User

router = APIRouter()

@router.post("/", response_model=SeasonRead, dependencies=[Depends(require_roles("admin"))])
def create(payload: SeasonCreate, request: Request, db: Session = Depends(get_db)):
    locale = request.headers.get("accept-language")
    if locale:
        locale = locale.split(",")[0].strip()
    return create_season(db, payload, locale)

@router.get("/active", response_model=SeasonRead | None)
def active(request: Request, db: Session = Depends(get_db)):
    locale = request.headers.get("accept-language")
    if locale:
        locale = locale.split(",")[0].strip()
    return get_active_season_localized(db, locale)