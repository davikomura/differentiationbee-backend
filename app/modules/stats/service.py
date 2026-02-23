from datetime import date, datetime, timedelta, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.modules.attempts.models import Attempt
from app.modules.sessions.models import GameSession


def _safe_accuracy(correct: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((correct / total) * 100, 2)


def _base_stats(db: Session, user_id: int) -> dict:
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

    return {
        "total_sessions": int(total_sessions),
        "total_attempts": total_attempts,
        "correct_attempts": correct_attempts,
        "accuracy_pct": _safe_accuracy(correct_attempts, total_attempts),
        "total_score": int(attempt_data.total_score or 0),
        "best_score": int(attempt_data.best_score or 0),
        "average_time_ms": int(attempt_data.average_time_ms or 0),
    }


def _activity_days(db: Session, user_id: int) -> list[date]:
    rows = (
        db.query(func.date(Attempt.created_at).label("d"))
        .filter(Attempt.user_id == user_id, Attempt.is_correct == True)  # noqa: E712
        .group_by(func.date(Attempt.created_at))
        .order_by(func.date(Attempt.created_at).asc())
        .all()
    )
    days: list[date] = []
    for row in rows:
        value = row.d
        if isinstance(value, datetime):
            days.append(value.date())
        else:
            days.append(value)
    return days


def _compute_streaks(days: list[date], today: date) -> tuple[int, int]:
    if not days:
        return 0, 0

    unique_days = sorted(set(days))

    best = 1
    running = 1
    for idx in range(1, len(unique_days)):
        if unique_days[idx] - unique_days[idx - 1] == timedelta(days=1):
            running += 1
        else:
            running = 1
        if running > best:
            best = running

    day_set = set(unique_days)
    cur = 0
    pivot = today
    while pivot in day_set:
        cur += 1
        pivot -= timedelta(days=1)

    return cur, best


def _avg_time_by_level(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(
            Attempt.level.label("level"),
            func.count(Attempt.id).label("attempts"),
            func.coalesce(func.avg(Attempt.time_taken_ms), 0).label("avg_time"),
        )
        .filter(Attempt.user_id == user_id)
        .group_by(Attempt.level)
        .order_by(Attempt.level.asc())
        .all()
    )

    return [
        {
            "level": int(row.level),
            "attempts": int(row.attempts or 0),
            "average_time_ms": int(row.avg_time or 0),
        }
        for row in rows
    ]


def my_stats(db: Session, user_id: int) -> dict:
    return _base_stats(db, user_id)


def my_advanced_stats(db: Session, user_id: int) -> dict:
    base = _base_stats(db, user_id)
    days = _activity_days(db, user_id)
    current_streak, best_streak = _compute_streaks(days, datetime.now(timezone.utc).date())

    return {
        **base,
        "current_streak_days": int(current_streak),
        "best_streak_days": int(best_streak),
        "average_time_ms_by_level": _avg_time_by_level(db, user_id),
    }


def my_evolution(db: Session, user_id: int, days: int = 30) -> dict:
    if days <= 0:
        days = 30
    if days > 365:
        days = 365

    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=days - 1)

    rows = (
        db.query(
            func.date(Attempt.created_at).label("d"),
            func.count(Attempt.id).label("attempts"),
            func.coalesce(func.sum(case((Attempt.is_correct == True, 1), else_=0)), 0).label("correct_attempts"),  # noqa: E712
            func.coalesce(func.sum(Attempt.score), 0).label("total_score"),
        )
        .filter(Attempt.user_id == user_id, Attempt.created_at >= datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc))
        .group_by(func.date(Attempt.created_at))
        .order_by(func.date(Attempt.created_at).asc())
        .all()
    )

    by_day: dict[date, dict] = {}
    for row in rows:
        day_value = row.d.date() if isinstance(row.d, datetime) else row.d
        attempts = int(row.attempts or 0)
        correct = int(row.correct_attempts or 0)
        by_day[day_value] = {
            "date": day_value.isoformat(),
            "attempts": attempts,
            "correct_attempts": correct,
            "accuracy_pct": _safe_accuracy(correct, attempts),
            "total_score": int(row.total_score or 0),
        }

    points: list[dict] = []
    cursor = start
    while cursor <= today:
        points.append(
            by_day.get(
                cursor,
                {
                    "date": cursor.isoformat(),
                    "attempts": 0,
                    "correct_attempts": 0,
                    "accuracy_pct": 0.0,
                    "total_score": 0,
                },
            )
        )
        cursor += timedelta(days=1)

    return {"days": days, "points": points}
