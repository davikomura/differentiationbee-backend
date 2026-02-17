from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.router import get_current_user
from app.modules.users.models import User

from app.modules.game.schemas import IssueQuestionRequest, IssuedQuestionRead
from app.modules.game.service import issue_question

router = APIRouter()

@router.post("/question", response_model=IssuedQuestionRead)
def get_question(payload: IssueQuestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    iq = issue_question(db, user_id=current_user.id, session_id=payload.session_id, level=payload.level)
    return {
        "question_id": iq.id,
        "session_id": iq.session_id,
        "level": iq.level,
        "expression_str": iq.expression_str,
        "expression_latex": iq.expression_latex,
        "issued_at": iq.issued_at,
    }