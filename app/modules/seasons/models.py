# app/modules/seasons/models.py
from sqlalchemy import Column, Integer, String, DateTime, Index, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, nullable=False)

    starts_at = Column(DateTime(timezone=True), nullable=False)
    ends_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    translations = relationship("SeasonTranslation", back_populates="season", cascade="all, delete-orphan", passive_deletes=True,)

Index("ix_seasons_window", Season.starts_at, Season.ends_at)

class SeasonTranslation(Base):
    __tablename__ = "season_translations"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)

    locale = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    season = relationship("Season", back_populates="translations")
    
    sessions = relationship(
        "GameSession",
        back_populates="season",
        cascade="all",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("season_id", "locale", name="uq_season_locale"),
        Index("ix_season_translations_locale", "locale"),
    )