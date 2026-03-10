from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.attempts.models import Attempt
from app.modules.auth.models import RefreshToken
from app.modules.game.models import IssuedQuestion
from app.modules.game.service import MAX_UNIQUE_DERIVATIVE_ATTEMPTS, issue_question
from app.modules.seasons.models import Season, SeasonTranslation
from app.modules.sessions.models import GameSession
from app.modules.tiers.models import Tier, TierTranslation
from app.modules.users.models import User


_ = (Attempt, RefreshToken, SeasonTranslation, Tier, TierTranslation)


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def seed_session_graph(db_session):
    season = Season(
        slug="season-1",
        starts_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        ends_at=datetime(2026, 3, 31, tzinfo=timezone.utc),
    )
    user = User(
        username="user1",
        email="user1@example.com",
        hashed_password="hash",
        role="user",
        points=0,
    )
    db_session.add_all([season, user])
    db_session.commit()

    session = GameSession(
        season_id=season.id,
        user_id=user.id,
        mode="practice",
        level=1,
        seed=100,
        is_active=True,
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    db_session.refresh(user)
    return user, session


def test_issue_question_retries_until_user_gets_new_derivative(db_session, monkeypatch):
    user, game_session = seed_session_graph(db_session)

    db_session.add(
        IssuedQuestion(
            user_id=user.id,
            session_id=game_session.id,
            level=1,
            expression_str="old",
            expression_latex="old",
            derivative_str="repeat-me",
            derivative_latex="repeat-me",
            time_limit_ms=35000,
        )
    )
    db_session.commit()

    generated = [
        {
            "expression_str": "expr-repeat",
            "expression_latex": "expr-repeat",
            "derivative_str": "repeat-me",
            "derivative_latex": "repeat-me",
        },
        {
            "expression_str": "expr-new",
            "expression_latex": "expr-new",
            "derivative_str": "brand-new",
            "derivative_latex": "brand-new",
        },
    ]
    calls = []

    def fake_generate_random_function(level: int, seed: int | None = None):
        calls.append((level, seed))
        payload = generated[min(len(calls) - 1, len(generated) - 1)].copy()
        payload["level"] = level
        return payload

    monkeypatch.setattr("app.modules.game.service.generate_random_function", fake_generate_random_function)

    issued = issue_question(db_session, user_id=user.id, session_id=game_session.id, level=1)

    assert issued.derivative_str == "brand-new"
    assert len(calls) == 2


def test_issue_question_retries_until_user_gets_new_expression(db_session, monkeypatch):
    user, game_session = seed_session_graph(db_session)

    db_session.add(
        IssuedQuestion(
            user_id=user.id,
            session_id=game_session.id,
            level=1,
            expression_str="same-expression",
            expression_latex="same-expression",
            derivative_str="old-derivative",
            derivative_latex="old-derivative",
            time_limit_ms=40000,
        )
    )
    db_session.commit()

    generated = [
        {
            "expression_str": "same-expression",
            "expression_latex": "same-expression",
            "derivative_str": "new-derivative-1",
            "derivative_latex": "new-derivative-1",
        },
        {
            "expression_str": "fresh-expression",
            "expression_latex": "fresh-expression",
            "derivative_str": "new-derivative-2",
            "derivative_latex": "new-derivative-2",
        },
    ]
    calls = []

    def fake_generate_random_function(level: int, seed: int | None = None):
        calls.append((level, seed))
        payload = generated[min(len(calls) - 1, len(generated) - 1)].copy()
        payload["level"] = level
        return payload

    monkeypatch.setattr("app.modules.game.service.generate_random_function", fake_generate_random_function)

    issued = issue_question(db_session, user_id=user.id, session_id=game_session.id, level=1)

    assert issued.expression_str == "fresh-expression"
    assert len(calls) == 2


def test_issue_question_falls_back_after_attempt_limit(db_session, monkeypatch):
    user, game_session = seed_session_graph(db_session)
    db_session.add(
        IssuedQuestion(
            user_id=user.id,
            session_id=game_session.id,
            level=1,
            expression_str="old",
            expression_latex="old",
            derivative_str="repeat-me",
            derivative_latex="repeat-me",
            time_limit_ms=35000,
        )
    )
    db_session.commit()

    calls = []

    def fake_generate_random_function(level: int, seed: int | None = None):
        calls.append((level, seed))
        return {
            "expression_str": f"expr-{len(calls)}",
            "expression_latex": f"expr-{len(calls)}",
            "derivative_str": "repeat-me",
            "derivative_latex": "repeat-me",
            "level": level,
        }

    monkeypatch.setattr("app.modules.game.service.generate_random_function", fake_generate_random_function)

    issued = issue_question(db_session, user_id=user.id, session_id=game_session.id, level=1)

    assert issued.derivative_str == "repeat-me"
    assert len(calls) == MAX_UNIQUE_DERIVATIVE_ATTEMPTS
