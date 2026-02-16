# app/models/user_stats.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    rating = Column(Integer, nullable=False, default=100)
    current_streak = Column(Integer, nullable=False, default=0)
    total_answered = Column(Integer, nullable=False, default=0)
    total_correct = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="stats")