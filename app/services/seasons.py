# app/services/seasons.py
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.season import Season
from app.models.user_season_stats import UserSeasonStats
from app.services.season_reset import soft_reset_rating

def get_active_season(db: Session) -> Season:
    season = db.query(Season).filter(Season.is_active.is_(True)).order_by(Season.starts_at.desc()).first()
    if not season:
        now = datetime.now(timezone.utc)
        season = Season(
            name=f"Temporada {now.year}-{now.month:02d}",
            starts_at=now,
            ends_at=None,
            is_active=True,
        )
        db.add(season)
        db.commit()
        db.refresh(season)
    return season

def get_previous_season(db: Session, active_season_id: int) -> Season | None:
    return (
        db.query(Season)
        .filter(Season.id != active_season_id)
        .order_by(Season.starts_at.desc())
        .first()
    )

def get_or_create_user_season_stats(db: Session, user_id: int) -> UserSeasonStats:
    season = get_active_season(db)

    current = (
        db.query(UserSeasonStats)
        .filter(UserSeasonStats.season_id == season.id, UserSeasonStats.user_id == user_id)
        .first()
    )
    if current:
        return current

    prev_season = get_previous_season(db, season.id)
    initial_rating = 100

    if prev_season:
        prev_stats = (
            db.query(UserSeasonStats)
            .filter(UserSeasonStats.season_id == prev_season.id, UserSeasonStats.user_id == user_id)
            .first()
        )
        if prev_stats:
            initial_rating = soft_reset_rating(int(prev_stats.rating))

    now = datetime.now(timezone.utc)
    sstats = UserSeasonStats(
        season_id=season.id,
        user_id=user_id,
        rating=int(initial_rating),
        current_streak=0,
        total_answered=0,
        total_correct=0,
        updated_at=now,
    )
    db.add(sstats)
    db.commit()
    db.refresh(sstats)
    return sstats

def start_new_season(db: Session, name: str, starts_at: datetime | None = None) -> Season:
    now = datetime.now(timezone.utc)
    db.query(Season).filter(Season.is_active.is_(True)).update({"is_active": False, "ends_at": now})
    db.commit()

    s = Season(
        name=name,
        starts_at=starts_at or now,
        ends_at=None,
        is_active=True,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s