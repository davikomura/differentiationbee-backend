# app/models/session.py
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class GameSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    score = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    average_time = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    is_finished = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="sessions")
    questions = relationship(
        "SessionQuestion",
        back_populates="session",
        cascade="all, delete",
    )
