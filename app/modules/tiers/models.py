# app/modules/tiers/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.db.base import Base

class Tier(Base):
    __tablename__ = "tiers"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    min_points = Column(Integer, nullable=False)
    max_points = Column(Integer, nullable=True)
    rank_order = Column(Integer, nullable=False)

    translations = relationship(
        "TierTranslation",
        back_populates="tier",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

Index("ix_tiers_range", Tier.min_points, Tier.max_points)

class TierTranslation(Base):
    __tablename__ = "tier_translations"

    id = Column(Integer, primary_key=True, index=True)
    tier_id = Column(Integer, ForeignKey("tiers.id", ondelete="CASCADE"), nullable=False)

    locale = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    tier = relationship("Tier", back_populates="translations")

    __table_args__ = (
        UniqueConstraint("tier_id", "locale", name="uq_tier_locale"),
        Index("ix_tier_translations_locale", "locale"),
    )