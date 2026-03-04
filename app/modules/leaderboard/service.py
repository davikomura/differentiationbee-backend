# app/modules/leaderboard/service.py
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.attempts.models import Attempt
from app.modules.sessions.models import GameSession
from app.modules.tiers.models import Tier
from app.modules.users.models import User


def _build_global_entries(users, start_rank: int = 1) -> list[dict]:
    return [
        {
            "rank": start_rank + idx,
            "user_id": row.id,
            "username": row.username,
            "points": int(row.points),
        }
        for idx, row in enumerate(users)
    ]


def global_leaderboard(db: Session, page: int = 1, limit: int = 50) -> dict:
    offset = (page - 1) * limit
    query = db.query(User.id, User.username, User.points)
    total = query.count()
    users = (
        query
        .order_by(User.points.desc(), User.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": _build_global_entries(users, start_rank=offset + 1),
        "page": page,
        "limit": limit,
        "total": total,
    }


def global_leaderboard_by_tier(db: Session, tier_key: str, page: int = 1, limit: int = 50) -> dict:
    tier = db.query(Tier).filter(Tier.key == tier_key).first()
    if not tier:
        return {
            "items": [],
            "page": page,
            "limit": limit,
            "total": 0,
        }

    query = (
        db.query(User.id, User.username, User.points)
        .filter(User.points >= tier.min_points)
    )

    if tier.max_points is not None:
        query = query.filter(User.points <= tier.max_points)

    offset = (page - 1) * limit
    total = query.count()
    users = (
        query
        .order_by(User.points.desc(), User.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": _build_global_entries(users, start_rank=offset + 1),
        "page": page,
        "limit": limit,
        "total": total,
    }


def season_leaderboard(db: Session, season_id: int, limit: int = 50) -> list[dict]:
    total_score = func.coalesce(func.sum(Attempt.score), 0)
    rows = (
        db.query(
            User.id.label("user_id"),
            User.username.label("username"),
            total_score.label("total_score"),
            func.count(func.distinct(GameSession.id)).label("sessions_played"),
        )
        .join(GameSession, GameSession.user_id == User.id)
        .outerjoin(Attempt, Attempt.session_id == GameSession.id)
        .filter(GameSession.season_id == season_id)
        .group_by(User.id, User.username)
        .order_by(total_score.desc(), User.username.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "rank": idx + 1,
            "user_id": row.user_id,
            "username": row.username,
            "total_score": int(row.total_score or 0),
            "sessions_played": int(row.sessions_played or 0),
        }
        for idx, row in enumerate(rows)
    ]
