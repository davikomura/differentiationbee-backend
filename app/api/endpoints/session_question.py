# app/api/endpoints/session_question.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.session_question import QuestionAnswerCreate
from app.models.session_question import SessionQuestion
from app.api.endpoints.auth import get_current_user
from app.models.user import User
from app.models.session import GameSession

import sympy as sp
from sympy.abc import x
from sympy.parsing.sympy_parser import parse_expr

router = APIRouter()

ALLOWED = {
    "x": x,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "pi": sp.pi,
    "E": sp.E,
}

def _parse_expr_safe(s: str):
    return parse_expr(
        s,
        local_dict=ALLOWED,
        global_dict={},
        evaluate=True
    )

@router.post("/track")
def track_question(
    payload: QuestionAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(GameSession).filter(
        GameSession.id == payload.session_id,
        GameSession.user_id == current_user.id
    ).first()

    if not session:
        return {"error": "Sessão inválida ou não pertence ao usuário"}

    try:
        original_expr = _parse_expr_safe(payload.question_str)
        correct_answer_str = str(sp.diff(original_expr, x))
    except Exception:
        correct_answer_str = ""

    question = SessionQuestion(
        session_id=payload.session_id,
        question_str=payload.question_str,
        correct_answer_str=correct_answer_str,
        user_answer=payload.user_answer,
        is_correct=payload.is_correct,
        time_taken=payload.time_taken
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    return {"message": "Resposta registrada com sucesso!", "question_id": question.id}