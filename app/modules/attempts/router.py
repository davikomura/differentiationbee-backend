from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.i18n import get_request_locale
from app.db.session import get_db
from app.modules.auth.router import get_current_user
from app.modules.users.models import User

from app.modules.attempts.schemas import AttemptCreate, AttemptResult
from app.modules.attempts.service import create_attempt_from_question

router = APIRouter()

@router.post("/", response_model=AttemptResult)
def create(payload: AttemptCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    attempt, correct_latex = create_attempt_from_question(
        db=db,
        user_id=current_user.id,
        question_id=payload.question_id,
        user_answer=payload.user_answer,
        time_taken_ms=payload.time_taken_ms,
        use_latex=payload.use_latex,
        locale=get_request_locale(request),
    )

    return {"attempt": attempt, "correct_derivative_latex": correct_latex}
