from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.i18n import t
from app.modules.attempts.models import Attempt
from app.modules.competitive.service import resolve_ranked_session
from app.modules.seasons.service import get_active_season
from app.modules.sessions.models import GameSession
from app.modules.tiers.service import (
    apply_points_change_with_soft_demotion,
    get_level_for_points,
    get_tier_for_points,
    tier_to_read,
)
from app.modules.users.models import User


def start_session(
    db: Session,
    user_id: int,
    mode: str = "practice",
    level: int | None = None,
    seed: int | None = None,
    locale: str = "en",
) -> GameSession:
    active = db.query(GameSession).filter(GameSession.user_id == user_id, GameSession.is_active == True).first()  # noqa: E712
    if active:
        raise HTTPException(status_code=409, detail=t("active_session_exists", locale))

    season = get_active_season(db)
    if not season:
        raise HTTPException(status_code=409, detail=t("no_active_season", locale))

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=t("user_not_found", locale))

    # Regra de negocio: cada tier corresponde a um nivel do gerador (1..12).
    derived_level = get_level_for_points(db, int(user.points or 0))

    s = GameSession(
        user_id=user_id,
        season_id=season.id,
        mode=mode,
        level=derived_level,
        seed=seed,
    )
    db.add(s)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=t("active_session_exists", locale))
    db.refresh(s)
    return s


def compute_speed_bonus_points(avg_time_ms: int, level: int) -> int:
    if avg_time_ms <= 0:
        return 0
    # target decresce com nivel mais alto (mais tolerancia a tempo maior)
    target_ms = 18000 + (int(level) * 1800)
    raw = int((target_ms - avg_time_ms) / 1800)
    return max(-12, min(12, raw))


def compute_session_points_delta(total_questions: int, correct_answers: int, level: int, avg_time_ms: int) -> int:
    if total_questions <= 0:
        return 0

    wrong = max(0, total_questions - correct_answers)
    gain_per_correct = 6 + int(level)
    penalty_per_wrong = 4 + int(level // 4)

    delta = (correct_answers * gain_per_correct) - (wrong * penalty_per_wrong)
    delta += compute_speed_bonus_points(avg_time_ms, level)
    if correct_answers >= wrong:
        delta += int(level)

    delta = max(-100, min(100, int(delta)))
    return int(delta)


def finish_session(db: Session, user_id: int, session_id: int, locale: str = "en") -> dict:
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=t("session_not_found", locale))

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=t("user_not_found", locale))

    points_before = int(getattr(user, "points", 0))
    tier_before = tier_to_read(get_tier_for_points(db, points_before), locale)
    wrong_answers = max(0, int(s.total_questions or 0) - int(s.correct_answers or 0))
    summary = f"{int(s.correct_answers or 0)}x{wrong_answers}"
    avg_time_ms = int(
        db.query(func.coalesce(func.avg(Attempt.time_taken_ms), 0))
        .filter(Attempt.session_id == s.id)
        .scalar()
        or 0
    )
    time_bonus_points = compute_speed_bonus_points(avg_time_ms, int(s.level or 1))

    if not s.is_active:
        points_after = points_before
        tier_after = tier_to_read(get_tier_for_points(db, points_after), locale)
        return {
            "session": s,
            "wrong_answers": wrong_answers,
            "result_summary": summary,
            "average_time_ms": avg_time_ms,
            "time_bonus_points": 0,
            "delta_points": 0,
            "points_before": points_before,
            "points_after": points_after,
            "tier_before": tier_before,
            "tier_after": tier_after,
        }

    s.is_active = False
    s.ended_at = datetime.now(timezone.utc)

    if s.mode == "ranked":
        delta = -20 if int(s.total_questions or 0) == 0 else 0
    else:
        delta = compute_session_points_delta(
            total_questions=int(s.total_questions or 0),
            correct_answers=int(s.correct_answers or 0),
            level=int(s.level or 1),
            avg_time_ms=avg_time_ms,
        )

    points_after = apply_points_change_with_soft_demotion(db, points_before, delta)
    user.points = points_after

    db.commit()
    db.refresh(s)

    if s.mode == "ranked":
        ranked_result = resolve_ranked_session(
            db,
            session_id=s.id,
            requester_user_id=user_id,
            locale=locale,
        )
        points_after = int(ranked_result.get("points_after", points_after))
        delta += int(ranked_result.get("delta_points", 0))

    tier_after = tier_to_read(get_tier_for_points(db, points_after), locale)

    return {
        "session": s,
        "wrong_answers": wrong_answers,
        "result_summary": summary,
        "average_time_ms": avg_time_ms,
        "time_bonus_points": time_bonus_points,
        "delta_points": delta,
        "points_before": points_before,
        "points_after": points_after,
        "tier_before": tier_before,
        "tier_after": tier_after,
    }


def get_session(db: Session, user_id: int, session_id: int, locale: str = "en") -> GameSession:
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=t("session_not_found", locale))
    return s


def list_sessions(db: Session, user_id: int, limit: int = 20) -> list[GameSession]:
    return (
        db.query(GameSession)
        .filter(GameSession.user_id == user_id)
        .order_by(GameSession.started_at.desc())
        .limit(limit)
        .all()
    )
