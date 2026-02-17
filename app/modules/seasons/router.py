from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.seasons.schemas import SeasonCreate, SeasonRead
from app.modules.seasons.service import create_season, get_active_season_localized

router = APIRouter()

@router.post("/", response_model=dict)
def create(payload: SeasonCreate, db: Session = Depends(get_db)):
    s = create_season(db, payload)
    return {"id": s.id, "slug": s.slug, "starts_at": s.starts_at, "ends_at": s.ends_at}

@router.get("/active", response_model=SeasonRead | None)
def active(request: Request, db: Session = Depends(get_db)):
    locale = request.headers.get("accept-language")
    if locale:
        locale = locale.split(",")[0].strip()
    return get_active_season_localized(db, locale)