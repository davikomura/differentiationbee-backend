from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.sessions.schemas import GameSessionCreate, GameSessionRead, SessionFinishResult
from app.modules.sessions.service import start_session, finish_session, get_session, list_sessions

from app.modules.auth.router import get_current_user
from app.modules.users.models import User

router = APIRouter()

@router.post("/start", response_model=GameSessionRead)
def start(payload: GameSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return start_session(db, user_id=current_user.id, mode=payload.mode, level=payload.level, seed=payload.seed)

@router.post("/{session_id}/finish", response_model=SessionFinishResult)
def finish(session_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    locale = request.headers.get("accept-language")
    locale = locale.split(",")[0].strip() if locale else "en"
    return finish_session(db, user_id=current_user.id, session_id=session_id, locale=locale)

@router.get("/{session_id}", response_model=GameSessionRead)
def read(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_session(db, user_id=current_user.id, session_id=session_id)

@router.get("/", response_model=list[GameSessionRead])
def list_my(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = 20):
    return list_sessions(db, user_id=current_user.id, limit=limit)