from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.router import get_current_user
from app.modules.stats.schemas import AdvancedStatsRead, EvolutionRead, MyStatsRead
from app.modules.stats.service import my_advanced_stats, my_evolution, my_stats
from app.modules.users.models import User

router = APIRouter()


@router.get("/me", response_model=MyStatsRead)
def read_my_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return my_stats(db, user_id=current_user.id)


@router.get("/me/advanced", response_model=AdvancedStatsRead)
def read_my_advanced_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return my_advanced_stats(db, user_id=current_user.id)


@router.get("/me/evolution", response_model=EvolutionRead)
def read_my_evolution(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return my_evolution(db, user_id=current_user.id, days=days)
