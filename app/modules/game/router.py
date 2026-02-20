from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.i18n import get_request_locale
from app.db.session import get_db
from app.modules.auth.router import get_current_user
from app.modules.users.models import User

from app.modules.game.schemas import DailyChallengeRead, IssueQuestionRequest, IssuedQuestionRead
from app.modules.game.service import get_daily_challenge, issue_question

router = APIRouter()


@router.get("/daily-challenge", response_model=DailyChallengeRead)
def daily_challenge():
    return get_daily_challenge()

@router.post("/question", response_model=IssuedQuestionRead)
def get_question(payload: IssueQuestionRequest, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    iq = issue_question(
        db,
        user_id=current_user.id,
        session_id=payload.session_id,
        level=payload.level,
        locale=get_request_locale(request),
    )
    return {
        "question_id": iq.id,
        "session_id": iq.session_id,
        "level": iq.level,
        "expression_str": iq.expression_str,
        "expression_latex": iq.expression_latex,
        "issued_at": iq.issued_at,
        "time_limit_ms": iq.time_limit_ms,
    }
