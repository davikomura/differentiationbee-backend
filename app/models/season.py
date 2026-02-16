# app/models/season.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("name", name="uq_seasons_name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user_stats = relationship("UserSeasonStats", back_populates="season", cascade="all, delete")