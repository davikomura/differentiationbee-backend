from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.i18n import t
from app.modules.game.generator import generate_random_function
from app.modules.game.models import IssuedQuestion
from app.modules.game.time_limits import get_time_limit_ms
from app.modules.sessions.models import GameSession


def issue_question(db: Session, user_id: int, session_id: int, level: int, locale: str = "en") -> IssuedQuestion:
    time_limit_ms = get_time_limit_ms(level)
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=t("session_not_found", locale))
    if not s.is_active:
        raise HTTPException(status_code=400, detail=t("session_closed", locale))

    if level < 1 or level > 12:
        raise HTTPException(status_code=400, detail=t("level_range_1_12", locale))

    q = generate_random_function(level=level)

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
