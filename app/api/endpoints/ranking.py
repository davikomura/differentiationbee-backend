# app/api/endpoints/ranking.py
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import func

from app.db.session import get_db
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.user_season_stats import UserSeasonStats
from app.services.seasons import get_active_season
from app.services.elo import get_arena_for_rating, arena_progress
from app.core.ratelimit import enforce_rate_limit, RateLimit

router = APIRouter()

class EloArenaInfo(BaseModel):
    index: int
    name: str
    min_rating: int
    max_rating: Optional[int] = None
    progress: Optional[float] = None

class RankingEloItem(BaseModel):
    username: str
    rating: int
    arena: EloArenaInfo
    total_answered: int
    total_correct: int
    winrate: float
    streak: int
    updated_at: str

@router.get("/elo/top", response_model=List[RankingEloItem])
def elo_top(request: Request, limit: int = 50, db: Session = Depends(get_db)):
    enforce_rate_limit(request, "ranking_elo_top", RateLimit(limit=120, window_seconds=60))
    season = get_active_season(db)

    rows = (
        db.query(User.username, UserSeasonStats)
        .join(UserSeasonStats, UserSeasonStats.user_id == User.id)
        .filter(UserSeasonStats.season_id == season.id)
        .order_by(UserSeasonStats.rating.desc(), UserSeasonStats.updated_at.desc())
        .limit(limit)
        .all()
    )

    out: list[RankingEloItem] = []
    for username, stats in rows:
        rating = int(stats.rating)
        arena = get_arena_for_rating(rating)
        prog = arena_progress(rating, arena)
        total_answered = int(stats.total_answered)
        total_correct = int(stats.total_correct)
        winrate = (total_correct / total_answered) if total_answered > 0 else 0.0

        out.append(
            RankingEloItem(
                username=username,
                rating=rating,
                arena=EloArenaInfo(
                    index=arena.index,
                    name=arena.name,
                    min_rating=int(prog["min"]),
                    max_rating=prog["max"],
                    progress=prog["pct"],
                ),
                total_answered=total_answered,
                total_correct=total_correct,
                winrate=round(winrate, 4),
                streak=int(stats.current_streak),
                updated_at=stats.updated_at.isoformat(),
            )
        )
    return out

@router.get("/elo/me")
def elo_me(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_rate_limit(request, "ranking_elo_me", RateLimit(limit=120, window_seconds=60))
    season = get_active_season(db)

    me_stats = (
        db.query(UserSeasonStats)
        .filter(UserSeasonStats.season_id == season.id, UserSeasonStats.user_id == current_user.id)
        .first()
    )
    if not me_stats:
        return {
            "season": {"id": season.id, "name": season.name},
            "rank": None,
            "total_players": int(db.query(func.count(UserSeasonStats.id)).filter(UserSeasonStats.season_id == season.id).scalar() or 0),
            "me": None,
        }

    my_rating = int(me_stats.rating)
    higher = (
        db.query(func.count(UserSeasonStats.id))
        .filter(UserSeasonStats.season_id == season.id, UserSeasonStats.rating > my_rating)
        .scalar()
        or 0
    )
    rank = int(higher) + 1
    total_players = int(db.query(func.count(UserSeasonStats.id)).filter(UserSeasonStats.season_id == season.id).scalar() or 0)

    arena = get_arena_for_rating(my_rating)
    prog = arena_progress(my_rating, arena)
    total_answered = int(me_stats.total_answered)
    total_correct = int(me_stats.total_correct)
    winrate = (total_correct / total_answered) if total_answered > 0 else 0.0

    return {
        "season": {"id": season.id, "name": season.name},
        "rank": rank,
        "total_players": total_players,
        "me": {
            "username": current_user.username,
            "rating": my_rating,
            "arena": {
                "index": arena.index,
                "name": arena.name,
                "min_rating": prog["min"],
                "max_rating": prog["max"],
                "progress": prog["pct"],
            },
            "total_answered": total_answered,
            "total_correct": total_correct,
            "winrate": round(winrate, 4),
            "streak": int(me_stats.current_streak),
            "updated_at": me_stats.updated_at.isoformat(),
        },
    }