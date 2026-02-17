# app/modules/tiers/router.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.tiers.schemas import TiersListRead, MyTierRead
from app.modules.tiers.service import list_tiers_localized, get_tier_for_points, _tier_to_read

from app.modules.auth.router import get_current_user
from app.modules.users.models import User

router = APIRouter()

@router.get("/", response_model=TiersListRead)
def list_all(request: Request, db: Session = Depends(get_db)):
    locale = request.headers.get("accept-language")
    if locale:
        locale = locale.split(",")[0].strip()
    items = list_tiers_localized(db, locale)
    return {"items": items}

@router.get("/me", response_model=MyTierRead)
def my_tier(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    locale = request.headers.get("accept-language")
    if locale:
        locale = locale.split(",")[0].strip()

    points = int(getattr(current_user, "points", 0))
    tier = get_tier_for_points(db, points)
    return {"points": points, "tier": _tier_to_read(tier, locale or "en")}