# app/modules/sessions/models.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True)
    
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="RESTRICT"), nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    mode = Column(String, nullable=False, default="practice")
    level = Column(Integer, nullable=True)
    seed = Column(Integer, nullable=True) 

    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    total_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="sessions")
    
    attempts = relationship(
        "app.modules.attempts.models.Attempt",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    issued_questions = relationship(
        "app.modules.game.models.IssuedQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    season = relationship("Season", back_populates="sessions")

Index("ix_game_sessions_user_started", GameSession.user_id, GameSession.started_at)
Index("ix_game_sessions_active", GameSession.user_id, GameSession.is_active)