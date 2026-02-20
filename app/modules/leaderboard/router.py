from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.leaderboard.schemas import LeaderboardEntry, SeasonLeaderboardEntry
from app.modules.leaderboard.service import global_leaderboard, season_leaderboard
from app.modules.seasons.service import get_active_season

router = APIRouter()


@router.get("/global", response_model=list[LeaderboardEntry])
def global_rank(db: Session = Depends(get_db), limit: int = Query(default=50, ge=1, le=200)):
    return global_leaderboard(db, limit=limit)


@router.get("/season/active", response_model=list[SeasonLeaderboardEntry])
def active_season_rank(db: Session = Depends(get_db), limit: int = Query(default=50, ge=1, le=200)):
    season = get_active_season(db)
    if not season:
        return []
    return season_leaderboard(db, season_id=season.id, limit=limit)


@router.get("/season/{season_id}", response_model=list[SeasonLeaderboardEntry])
def season_rank(season_id: int, db: Session = Depends(get_db), limit: int = Query(default=50, ge=1, le=200)):
    return season_leaderboard(db, season_id=season_id, limit=limit)
