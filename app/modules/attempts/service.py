# app/modules/attempts/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.modules.attempts.models import Attempt
from app.modules.game.models import IssuedQuestion
from app.modules.sessions.models import GameSession
from app.modules.game.validator import validate_answer


def create_attempt_from_question(
    db: Session,
    user_id: int,
    question_id: int,
    user_answer: str,
    time_taken_ms: int,
    use_latex: bool,
) -> tuple[Attempt, str]:
    if time_taken_ms <= 0 or time_taken_ms > 10 * 60 * 1000:
        raise HTTPException(status_code=400, detail="time_taken_ms inválido")

    q = (
        db.query(IssuedQuestion)
        .filter(IssuedQuestion.id == question_id, IssuedQuestion.user_id == user_id)
        .first()
    )
    if not q:
        raise HTTPException(status_code=404, detail="Questão não encontrada")

    if q.answered:
        raise HTTPException(status_code=409, detail="Questão já foi respondida")

    s = db.query(GameSession).filter(GameSession.id == q.session_id, GameSession.user_id == user_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    if not s.is_active:
        raise HTTPException(status_code=400, detail="Sessão encerrada")

    result = validate_answer(
        correct_derivative_str=q.derivative_str,
        user_input_str=user_answer,
        time_taken=float(time_taken_ms) / 1000.0,
        level=q.level,
        use_latex=use_latex,
    )

    is_correct = bool(result.get("is_correct", False))
    score = int(result.get("score", 0))
    correct_derivative_latex = result.get("correct_derivative_latex") or (q.derivative_latex or "")

    q.answered = True
    q.answered_at = datetime.now(timezone.utc)

    attempt = Attempt(
        user_id=user_id,
        session_id=q.session_id,
        issued_question_id=q.id,
        level=q.level,
        expression_str=q.expression_str,
        expression_latex=q.expression_latex,
        derivative_latex=q.derivative_latex,
        user_answer=user_answer,
        use_latex=use_latex,
        is_correct=is_correct,
        score=score,
        time_taken_ms=time_taken_ms,
    )
    db.add(attempt)

    s.total_questions += 1
    if is_correct:
        s.correct_answers += 1
        s.total_score += score

    db.commit()
    db.refresh(attempt)
    return attempt, correct_derivative_latex