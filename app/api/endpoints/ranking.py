# app/api/endpoints/ranking.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from app.models.session import GameSession
from app.db.session import get_db
from app.api.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()

class RankingItem(BaseModel):
    username: str
    score: int
    correct_answers: int
    average_time: float
    created_at: str

class SaveSessionRequest(BaseModel):
    session_id: int
    score: int
    correct_answers: int
    average_time: float
    
@router.post("/start")
def start_new_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = GameSession(user_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"message": "Sessão iniciada", "session_id": session.id}

@router.get("/top", response_model=List[RankingItem])
def get_top_ranking(limit: int = 10, db: Session = Depends(get_db)):
    sessions = (
        db.query(GameSession)
        .join(GameSession.user)
        .order_by(GameSession.score.desc())
        .limit(limit)
        .all()
    )

    return [
        RankingItem(
            username=s.user.username,
            score=s.score,
            correct_answers=s.correct_answers,
            average_time=round(s.average_time, 2),
            created_at=s.created_at.isoformat()
        )
        for s in sessions
    ]

@router.post("/save")
def save_session(payload: SaveSessionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(GameSession).filter_by(id=payload.session_id, user_id=current_user.id).first()
    
    if not session:
        return {"error": "Sessão não encontrada"}, 404

    session.score = payload.score
    session.correct_answers = payload.correct_answers
    session.average_time = payload.average_time
    
    db.commit()
    db.refresh(session)

    return {"message": "Session updated!", "session_id": session.id}

@router.get("/my", response_model=List[RankingItem])
def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = (
        db.query(GameSession)
        .filter(GameSession.user_id == current_user.id)
        .order_by(GameSession.created_at.desc())
        .all()
    )

    return [
        RankingItem(
            username=current_user.username,
            score=s.score,
            correct_answers=s.correct_answers,
            average_time=round(s.average_time, 2),
            created_at=s.created_at.isoformat()
        )
        for s in sessions
    ]
