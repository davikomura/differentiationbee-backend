from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.i18n import t
from app.modules.game.generator import generate_random_function
from app.modules.game.models import IssuedQuestion
from app.modules.game.time_limits import get_time_limit_ms
from app.modules.sessions.models import GameSession

MAX_UNIQUE_DERIVATIVE_ATTEMPTS = 64


def _has_seen_expression(db: Session, user_id: int, expression_str: str) -> bool:
    return (
        db.query(IssuedQuestion.id)
        .filter(IssuedQuestion.user_id == user_id, IssuedQuestion.expression_str == expression_str)
        .first()
        is not None
    )


def _has_seen_derivative(db: Session, user_id: int, derivative_str: str) -> bool:
    return (
        db.query(IssuedQuestion.id)
        .filter(IssuedQuestion.user_id == user_id, IssuedQuestion.derivative_str == derivative_str)
        .first()
        is not None
    )


def _is_new_question_for_user(db: Session, user_id: int, candidate: dict) -> bool:
    return not _has_seen_expression(db, user_id, candidate["expression_str"]) and not _has_seen_derivative(
        db,
        user_id,
        candidate["derivative_str"],
    )


def _generate_question_for_user(db: Session, user_id: int, level: int, base_seed: int | None) -> dict:
    first_candidate: dict | None = None

    for attempt in range(MAX_UNIQUE_DERIVATIVE_ATTEMPTS):
        seed = None if base_seed is None else base_seed + attempt
        candidate = generate_random_function(level=level, seed=seed)
        if first_candidate is None:
            first_candidate = candidate
        if _is_new_question_for_user(db, user_id, candidate):
            return candidate

    return first_candidate or generate_random_function(level=level, seed=base_seed)


def issue_question(db: Session, user_id: int, session_id: int, level: int | None, locale: str = "en") -> IssuedQuestion:
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=t("session_not_found", locale))
    if not s.is_active:
        raise HTTPException(status_code=400, detail=t("session_closed", locale))

    # Regra de negocio: nivel da questao sempre segue nivel da sessao (tier do usuario).
    session_level = int(s.level or level or 1)
    level = session_level

    if level < 1 or level > 12:
        raise HTTPException(status_code=400, detail=t("level_range_1_12", locale))

    time_limit_ms = get_time_limit_ms(level)
    seed = None
    if s.seed is not None:
        issued_count = (
            db.query(func.count(IssuedQuestion.id))
            .filter(IssuedQuestion.session_id == session_id)
            .scalar()
            or 0
        )
        seed = int(s.seed) + int(issued_count) * 9973 + int(level) * 131

    q = _generate_question_for_user(db, user_id=user_id, level=level, base_seed=seed)

    iq = IssuedQuestion(
        user_id=user_id,
        session_id=session_id,
        level=level,
        expression_str=q["expression_str"],
        expression_latex=q["expression_latex"],
        derivative_str=q["derivative_str"],
        derivative_latex=q["derivative_latex"],
        issued_at=datetime.now(timezone.utc),
        time_limit_ms=time_limit_ms,
    )

    db.add(iq)
    db.commit()
    db.refresh(iq)
    return iq


def get_daily_challenge(date_utc: datetime | None = None) -> dict:
    now = date_utc or datetime.now(timezone.utc)
    day_index = now.date().toordinal()
    level = (day_index % 12) + 1
    q = generate_random_function(level=level, seed=day_index)
    return {
        "challenge_date": now.date().isoformat(),
        "level": level,
        "expression_str": q["expression_str"],
        "expression_latex": q["expression_latex"],
    }
