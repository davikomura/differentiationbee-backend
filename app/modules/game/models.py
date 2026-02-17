from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base


class IssuedQuestion(Base):
    __tablename__ = "issued_questions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)

    level = Column(Integer, nullable=False)

    expression_str = Column(Text, nullable=False)
    expression_latex = Column(Text, nullable=True)

    # guardamos a derivada correta aqui (NÃO mandamos pro client)
    derivative_str = Column(Text, nullable=False)
    derivative_latex = Column(Text, nullable=True)

    issued_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # evita reuso / replay
    answered = Column(Boolean, default=False, nullable=False)
    answered_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("GameSession", back_populates="issued_questions")


Index("ix_issued_questions_user_session", IssuedQuestion.user_id, IssuedQuestion.session_id)
Index("ix_issued_questions_session_issued", IssuedQuestion.session_id, IssuedQuestion.issued_at)