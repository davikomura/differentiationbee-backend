from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    refresh_tokens = relationship(
        "app.modules.auth.models.RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    
    sessions = relationship(
        "app.modules.sessions.models.GameSession",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )