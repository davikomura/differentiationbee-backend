# app/models/question_instance.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class QuestionInstance(Base):
    __tablename__ = "question_instances"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)

    level = Column(Integer, nullable=False)

    arena_index = Column(Integer, nullable=False)
    arena_name = Column(String, nullable=False)
    rating_at_issue = Column(Integer, nullable=False)

    expression_str = Column(String, nullable=False)
    expression_latex = Column(String, nullable=False)
    expression_hash = Column(String(64), nullable=False, index=True)

    correct_derivative_str = Column(String, nullable=False)
    correct_derivative_latex = Column(String, nullable=False)

    issued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    answered = Column(Boolean, default=False, nullable=False)

    session = relationship("GameSession", back_populates="question_instances")
    answer = relationship("SessionQuestion", back_populates="question_instance", uselist=False)

Index("ix_qi_session_issued", QuestionInstance.session_id, QuestionInstance.issued_at)
Index("ix_qi_session_hash", QuestionInstance.session_id, QuestionInstance.expression_hash)