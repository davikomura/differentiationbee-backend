# app/api/endpoints/seasons.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.seasons import get_active_season, start_new_season

router = APIRouter()

class StartSeasonRequest(BaseModel):
    name: str

@router.get("/current")
def current_season(db: Session = Depends(get_db)):
    s = get_active_season(db)
    return {
        "id": s.id,
        "name": s.name,
        "starts_at": s.starts_at.isoformat(),
        "ends_at": s.ends_at.isoformat() if s.ends_at else None,
        "is_active": s.is_active,
    }

@router.post("/start")
def start_season(payload: StartSeasonRequest, db: Session = Depends(get_db)):
    s = start_new_season(db, payload.name)
    return {
        "id": s.id,
        "name": s.name,
        "starts_at": s.starts_at.isoformat(),
        "ends_at": s.ends_at.isoformat() if s.ends_at else None,
        "is_active": s.is_active,
    }