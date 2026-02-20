from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.router import get_current_user
from app.modules.stats.schemas import MyStatsRead
from app.modules.stats.service import my_stats
from app.modules.users.models import User

router = APIRouter()


@router.get("/me", response_model=MyStatsRead)
def read_my_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return my_stats(db, user_id=current_user.id)
