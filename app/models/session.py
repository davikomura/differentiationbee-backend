# app/models/session.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class GameSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    score = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    average_time = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    is_finished = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="sessions")
    questions = relationship(
        "SessionQuestion",
        back_populates="session",
        cascade="all, delete",
    )
    question_instances = relationship(
        "QuestionInstance",
        back_populates="session",
        cascade="all, delete",
    )

Index("ix_sessions_finished_score", GameSession.is_finished, GameSession.score)