from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.modules.game.time_limits import get_time_limit_ms
from app.modules.sessions.models import GameSession
from app.modules.game.generator import generate_random_function
from app.modules.game.models import IssuedQuestion


def issue_question(db: Session, user_id: int, session_id: int, level: int) -> IssuedQuestion:
    time_limit_ms = get_time_limit_ms(level)
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    if not s.is_active:
        raise HTTPException(status_code=400, detail="Sessão encerrada")

    if level < 1 or level > 10:
        raise HTTPException(status_code=400, detail="level deve estar entre 1 e 10")

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