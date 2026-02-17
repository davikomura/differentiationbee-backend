from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)

    issued_question_id = Column(Integer, ForeignKey("issued_questions.id", ondelete="CASCADE"), nullable=False)

    level = Column(Integer, nullable=False)

    expression_str = Column(Text, nullable=False)
    expression_latex = Column(Text, nullable=True)
    derivative_latex = Column(Text, nullable=True)

    user_answer = Column(Text, nullable=False)
    use_latex = Column(Boolean, default=False, nullable=False)

    is_correct = Column(Boolean, default=False, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    time_taken_ms = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("GameSession", back_populates="attempts")
    question = relationship("IssuedQuestion")


Index("ix_attempts_session_created", Attempt.session_id, Attempt.created_at)
Index("ix_attempts_user_created", Attempt.user_id, Attempt.created_at)