from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.attempts.models import Attempt
from app.modules.auth.models import RefreshToken
from app.modules.game.models import IssuedQuestion
from app.modules.seasons.models import Season, SeasonTranslation
from app.modules.seasons.schemas import SeasonCreate, SeasonTranslationCreate
from app.modules.seasons.service import create_season
from app.modules.sessions.models import GameSession
from app.modules.tiers.models import Tier, TierTranslation
from app.modules.users.models import User


_ = (Attempt, RefreshToken, IssuedQuestion, GameSession, Tier, TierTranslation, User)


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine, tables=[Season.__table__, SeasonTranslation.__table__])
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def make_payload(*, slug: str, starts_at: datetime, ends_at: datetime) -> SeasonCreate:
    return SeasonCreate(
        slug=slug,
        starts_at=starts_at,
        ends_at=ends_at,
        translations=[
            SeasonTranslationCreate(locale="pt-BR", title="Temporada 1", description="Descricao PT"),
            SeasonTranslationCreate(locale="en", title="Season 1", description="EN description"),
            SeasonTranslationCreate(locale="es", title="Temporada 1 ES", description="Descripcion ES"),
        ],
    )


def test_create_season_is_idempotent_for_same_payload(db_session):
    starts_at = datetime(2026, 3, 1, tzinfo=timezone.utc)
    ends_at = datetime(2026, 3, 31, tzinfo=timezone.utc)
    payload = make_payload(slug="season-2026-03", starts_at=starts_at, ends_at=ends_at)

    created = create_season(db_session, payload, "pt-BR")
    repeated = create_season(db_session, payload, "pt-BR")

    assert repeated["id"] == created["id"]
    assert db_session.query(Season).count() == 1


def test_create_season_rejects_exact_window_with_different_payload(db_session):
    starts_at = datetime(2026, 4, 1, tzinfo=timezone.utc)
    ends_at = datetime(2026, 4, 30, tzinfo=timezone.utc)

    create_season(db_session, make_payload(slug="season-2026-04", starts_at=starts_at, ends_at=ends_at), "pt-BR")

    conflicting = make_payload(slug="season-2026-04-v2", starts_at=starts_at, ends_at=ends_at)

    with pytest.raises(HTTPException) as exc:
        create_season(db_session, conflicting, "pt-BR")

    assert exc.value.status_code == 409
    assert exc.value.detail == "Ja existe uma season com esse recorte temporal"


def test_create_season_rejects_overlapping_window(db_session):
    starts_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    ends_at = datetime(2026, 5, 31, tzinfo=timezone.utc)
    create_season(db_session, make_payload(slug="season-2026-05", starts_at=starts_at, ends_at=ends_at), "pt-BR")

    overlapping = make_payload(
        slug="season-2026-05-b",
        starts_at=starts_at + timedelta(days=10),
        ends_at=ends_at + timedelta(days=10),
    )

    with pytest.raises(HTTPException) as exc:
        create_season(db_session, overlapping, "pt-BR")

    assert exc.value.status_code == 409
    assert exc.value.detail == "O recorte temporal da season sobrepoe outra season existente"
