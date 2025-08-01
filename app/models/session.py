from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.session import Base

class GameSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    score = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    average_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
