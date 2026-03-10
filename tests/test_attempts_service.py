from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.modules.attempts.models import Attempt
from app.modules.attempts.service import create_attempt_from_question
from app.modules.auth.models import RefreshToken
from app.modules.game.models import IssuedQuestion
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


def seed_attempt_graph(db_session):
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

    question = IssuedQuestion(
        user_id=user.id,
        session_id=session.id,
        level=1,
        expression_str="3*x**2 + 5*x",
        expression_latex="3 x^2 + 5 x",
        derivative_str="6*x + 5",
        derivative_latex="6 x + 5",
        issued_at=datetime.utcnow() - timedelta(seconds=1),
        time_limit_ms=40000,
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(session)
    db_session.refresh(question)
    db_session.refresh(user)
    return user, session, question


def test_create_attempt_updates_session_total_score(db_session):
    user, session, question = seed_attempt_graph(db_session)

    attempt, _ = create_attempt_from_question(
        db=db_session,
        user_id=user.id,
        question_id=question.id,
        user_answer="6*x + 5",
        time_taken_ms=2000,
        use_latex=False,
    )

    db_session.refresh(session)

    assert attempt.is_correct is True
    assert attempt.score > 0
    assert session.total_score == attempt.score
