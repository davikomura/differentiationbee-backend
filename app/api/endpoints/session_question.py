# app/api/endpoints/session_question.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import get_db
from app.schemas.session_question import QuestionAnswerCreate
from app.models.session_question import SessionQuestion
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.session import GameSession
from app.models.user_stats import UserStats
from app.models.question_instance import QuestionInstance
from app.services.validator import validate_answer
from app.services.elo import compute_rating_delta, get_arena_for_rating, arena_progress
from app.services.seasons import get_or_create_user_season_stats, get_active_season
from app.core.ratelimit import enforce_rate_limit, RateLimit

router = APIRouter()

@router.post("/track")
def track_question(
    request: Request,
    payload: QuestionAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "track", RateLimit(limit=90, window_seconds=60))

    qi = db.query(QuestionInstance).filter(QuestionInstance.id == payload.question_instance_id).first()
    if not qi:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    session = db.query(GameSession).filter(
        GameSession.id == qi.session_id,
        GameSession.user_id == current_user.id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão inválida ou não pertence ao usuário")

    if session.is_finished:
        raise HTTPException(status_code=400, detail="Sessão já finalizada")

    if qi.answered:
        raise HTTPException(status_code=409, detail="Questão já respondida")

    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).with_for_update().first()
    if not stats:
        stats = UserStats(user_id=current_user.id, rating=100)
        db.add(stats)
        db.commit()
        stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).with_for_update().first()

    sstats = get_or_create_user_season_stats(db, current_user.id)
    sstats = (
        db.query(type(sstats))
        .filter(type(sstats).id == sstats.id)
        .with_for_update()
        .first()
    )

    season = get_active_season(db)

    now = datetime.now(timezone.utc)
    time_taken = max(0.0, (now - qi.issued_at).total_seconds())

    result = validate_answer(
        correct_derivative_str=qi.correct_derivative_str,
        user_input_str=payload.user_answer,
        time_taken=time_taken,
        level=qi.level,
        use_latex=payload.use_latex,
    )

    is_correct = bool(result.get("is_correct", False))
    score = int(result.get("score", 0))
    correct_derivative_latex = str(result.get("correct_derivative_latex") or qi.correct_derivative_latex)
    error = result.get("error")

    delta = compute_rating_delta(is_correct=is_correct, level=qi.level, time_taken=time_taken)

    def apply_delta(obj):
        before = int(obj.rating)
        after = max(0, before + int(delta))
        if is_correct:
            obj.current_streak = int(obj.current_streak) + 1
            obj.total_correct = int(obj.total_correct) + 1
        else:
            obj.current_streak = 0
        obj.total_answered = int(obj.total_answered) + 1
        obj.rating = int(after)
        obj.updated_at = datetime.now(timezone.utc)
        return before, after

    lifetime_before, lifetime_after = apply_delta(stats)
    season_before, season_after = apply_delta(sstats)

    arena_now = get_arena_for_rating(season_after)
    prog = arena_progress(season_after, arena_now)

    q = SessionQuestion(
        session_id=qi.session_id,
        question_instance_id=qi.id,
        question_str=qi.expression_str,
        correct_answer_str=qi.correct_derivative_str,
        correct_answer_latex=qi.correct_derivative_latex,
        user_answer=payload.user_answer,
        is_correct=is_correct,
        time_taken=time_taken,
        level=qi.level,
        score=score,
        rating_before=season_before,
        rating_after=season_after,
        rating_delta=int(delta),
        arena_index=int(arena_now.index),
        arena_name=str(arena_now.name),
    )

    qi.answered = True

    db.add(q)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Questão já registrada")

    return {
        "message": "Resposta registrada",
        "question_id": q.id,
        "is_correct": is_correct,
        "score": score,
        "time_taken": round(time_taken, 3),
        "level": q.level,
        "correct_derivative_latex": correct_derivative_latex,
        "error": error,
        "season": {"id": season.id, "name": season.name},
        "elo": {"before": season_before, "delta": int(delta), "after": season_after},
        "arena": {"index": arena_now.index, "name": arena_now.name, "min_rating": prog["min"], "max_rating": prog["max"], "progress": prog["pct"]},
        "streak": int(sstats.current_streak),
        "lifetime_elo": {"before": lifetime_before, "after": lifetime_after},
    }