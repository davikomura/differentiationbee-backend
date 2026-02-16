# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.db.session import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    sessions = relationship(
        "GameSession",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    stats = relationship(
        "UserStats",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    season_stats = relationship(
        "UserSeasonStats",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )