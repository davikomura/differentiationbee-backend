# app/modules/sessions/service.py
import math
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.modules.sessions.models import GameSession
from app.modules.tiers.service import apply_points_change_with_soft_demotion, get_tier_for_points, tier_to_read
from app.modules.users.models import User

def start_session(db: Session, user_id: int, mode: str = "practice", level: int | None = None, seed: int | None = None) -> GameSession:
    active = db.query(GameSession).filter(GameSession.user_id == user_id, GameSession.is_active == True).first()
    if active:
        raise HTTPException(status_code=409, detail="Já existe uma sessão ativa para este usuário")

    s = GameSession(user_id=user_id, mode=mode, level=level, seed=seed)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def compute_session_points_delta(total_score: int, total_questions: int, correct_answers: int) -> int:
    if total_questions <= 0:
        return 0

    wrong = total_questions - correct_answers
    accuracy = correct_answers / total_questions

    base = int(math.sqrt(max(total_score, 0)))
    mult = 0.5 + accuracy
    gain = int(base * mult)

    penalty = 3 * wrong
    delta = gain - penalty

    delta = max(-80, min(60, delta))
    return int(delta)

def finish_session(db: Session, user_id: int, session_id: int, locale: str = "en") -> dict:
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    points_before = int(getattr(user, "points", 0))
    tier_before = tier_to_read(get_tier_for_points(db, points_before), locale)

    if not s.is_active:
        points_after = points_before
        tier_after = tier_to_read(get_tier_for_points(db, points_after), locale)
        return {
            "session": s,
            "delta_points": 0,
            "points_before": points_before,
            "points_after": points_after,
            "tier_before": tier_before,
            "tier_after": tier_after,
        }

    s.is_active = False
    s.ended_at = datetime.now(timezone.utc)

    delta = compute_session_points_delta(
        total_score=s.total_score,
        total_questions=s.total_questions,
        correct_answers=s.correct_answers,
    )

    points_after = apply_points_change_with_soft_demotion(db, points_before, delta)
    user.points = points_after

    db.commit()
    db.refresh(s)

    tier_after = tier_to_read(get_tier_for_points(db, points_after), locale)

    return {
        "session": s,
        "delta_points": delta,
        "points_before": points_before,
        "points_after": points_after,
        "tier_before": tier_before,
        "tier_after": tier_after,
    }

def get_session(db: Session, user_id: int, session_id: int) -> GameSession:
    s = db.query(GameSession).filter(GameSession.id == session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return s

def list_sessions(db: Session, user_id: int, limit: int = 20) -> list[GameSession]:
    return (
        db.query(GameSession)
        .filter(GameSession.user_id == user_id)
        .order_by(GameSession.started_at.desc())
        .limit(limit)
        .all()
    )