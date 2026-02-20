from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.sessions.models import GameSession
from app.modules.users.models import User


def global_leaderboard(db: Session, limit: int = 50) -> list[dict]:
    users = (
        db.query(User.id, User.username, User.points)
        .order_by(User.points.desc(), User.created_at.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "rank": idx + 1,
            "user_id": row.id,
            "username": row.username,
            "points": int(row.points),
        }
        for idx, row in enumerate(users)
    ]


def season_leaderboard(db: Session, season_id: int, limit: int = 50) -> list[dict]:
    rows = (
        db.query(
            User.id.label("user_id"),
            User.username.label("username"),
            func.coalesce(func.sum(GameSession.total_score), 0).label("total_score"),
            func.count(GameSession.id).label("sessions_played"),
        )
        .join(GameSession, GameSession.user_id == User.id)
        .filter(GameSession.season_id == season_id)
        .group_by(User.id, User.username)
        .order_by(func.sum(GameSession.total_score).desc(), User.username.asc())
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
