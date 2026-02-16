# app/models/session_question.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.session import Base

class SessionQuestion(Base):
    __tablename__ = "session_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)

    question_instance_id = Column(String(36), ForeignKey("question_instances.id", ondelete="CASCADE"), nullable=False, unique=True)

    question_str = Column(String, nullable=False)
    correct_answer_str = Column(String, nullable=False)
    correct_answer_latex = Column(String, nullable=False)
    user_answer = Column(String, nullable=False)

    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, nullable=False)
    level = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False, default=0)

    rating_before = Column(Integer, nullable=False, default=0)
    rating_after = Column(Integer, nullable=False, default=0)
    rating_delta = Column(Integer, nullable=False, default=0)
    arena_index = Column(Integer, nullable=False, default=1)
    arena_name = Column(String, nullable=False, default="Vale dos Polinômios")

    session = relationship("GameSession", back_populates="questions")
    question_instance = relationship("QuestionInstance", back_populates="answer")

Index("ix_session_questions_session", SessionQuestion.session_id)