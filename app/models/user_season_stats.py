# app/models/user_season_stats.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class UserSeasonStats(Base):
    __tablename__ = "user_season_stats"
    __table_args__ = (UniqueConstraint("season_id", "user_id", name="uq_user_season_stats_season_user"),)

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    rating = Column(Integer, nullable=False, default=100)
    current_streak = Column(Integer, nullable=False, default=0)
    total_answered = Column(Integer, nullable=False, default=0)
    total_correct = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    season = relationship("Season", back_populates="user_stats")
    user = relationship("User", back_populates="season_stats")