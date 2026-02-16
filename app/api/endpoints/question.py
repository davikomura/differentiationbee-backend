# app/api/endpoints/question.py
import uuid
import os
import hashlib
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.session import GameSession
from app.models.question_instance import QuestionInstance
from app.services.generator import generate_random_function
from app.services.elo import get_arena_for_rating, pick_level_for_arena, arena_progress
from app.services.seasons import get_or_create_user_season_stats

router = APIRouter()

MAX_GEN_ATTEMPTS = int(os.getenv("MAX_GEN_ATTEMPTS") or "12")
RECENT_DEDUP_LIMIT = int(os.getenv("RECENT_DEDUP_LIMIT") or "200")

def _hash_expr(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

@router.get("/generate")
def generate_question(
    session_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(GameSession).filter(
        GameSession.id == session_id,
        GameSession.user_id == current_user.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    if session.is_finished:
        raise HTTPException(status_code=400, detail="Sessão já finalizada")

    sstats = get_or_create_user_season_stats(db, current_user.id)

    arena = get_arena_for_rating(int(sstats.rating))
    level = pick_level_for_arena(arena)

    recent_hashes = (
        db.query(QuestionInstance.expression_hash)
        .join(GameSession, GameSession.id == QuestionInstance.session_id)
        .filter(GameSession.user_id == current_user.id)
        .order_by(QuestionInstance.issued_at.desc())
        .limit(RECENT_DEDUP_LIMIT)
        .all()
    )
    recent_set = {h[0] for h in recent_hashes if h and h[0]}

    chosen = None
    for _ in range(MAX_GEN_ATTEMPTS):
        data = generate_random_function(int(level))
        h = _hash_expr(data["expression_str"])
        if h in recent_set:
            continue
        chosen = (data, h)
        break

    if chosen is None:
        data = generate_random_function(int(level))
        h = _hash_expr(data["expression_str"])
        chosen = (data, h)

    data, expr_hash = chosen

    qi = QuestionInstance(
        id=str(uuid.uuid4()),
        session_id=session.id,
        level=int(level),
        arena_index=int(arena.index),
        arena_name=str(arena.name),
        rating_at_issue=int(sstats.rating),
        expression_str=data["expression_str"],
        expression_latex=data["expression_latex"],
        expression_hash=str(expr_hash),
        correct_derivative_str=data["derivative_str"],
        correct_derivative_latex=data["derivative_latex"],
    )
    db.add(qi)
    db.commit()
    db.refresh(qi)

    prog = arena_progress(int(sstats.rating), arena)

    return {
        "question_instance_id": qi.id,
        "expression_latex": qi.expression_latex,
        "expression_str": qi.expression_str,
        "level": qi.level,
        "arena": {
            "index": arena.index,
            "name": arena.name,
            "rating": int(sstats.rating),
            "min_rating": prog["min"],
            "max_rating": prog["max"],
            "progress": prog["pct"],
        },
    }