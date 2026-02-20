from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.modules.attempts.models import Attempt
from app.modules.sessions.models import GameSession


def my_stats(db: Session, user_id: int) -> dict:
    total_sessions = db.query(func.count(GameSession.id)).filter(GameSession.user_id == user_id).scalar() or 0

    attempt_data = (
        db.query(
            func.count(Attempt.id).label("total_attempts"),
            func.coalesce(func.sum(case((Attempt.is_correct == True, 1), else_=0)), 0).label("correct_attempts"),  # noqa: E712
            func.coalesce(func.sum(Attempt.score), 0).label("total_score"),
            func.coalesce(func.max(Attempt.score), 0).label("best_score"),
            func.coalesce(func.avg(Attempt.time_taken_ms), 0).label("average_time_ms"),
        )
        .filter(Attempt.user_id == user_id)
        .one()
    )

    total_attempts = int(attempt_data.total_attempts or 0)
    correct_attempts = int(attempt_data.correct_attempts or 0)
    accuracy_pct = round((correct_attempts / total_attempts) * 100, 2) if total_attempts else 0.0

    return {
        "total_sessions": int(total_sessions),
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy_pct": accuracy_pct,
        "total_score": int(attempt_data.total_score or 0),
        "best_score": int(attempt_data.best_score or 0),
        "average_time_ms": int(attempt_data.average_time_ms or 0),
    }
