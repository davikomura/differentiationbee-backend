from __future__ import annotations

import random
import time
import uuid

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.i18n import t
from app.core.state_backends import get_competitive_store
from app.modules.attempts.models import Attempt
from app.modules.seasons.service import get_active_season
from app.modules.sessions.models import GameSession
from app.modules.tiers.service import get_level_for_points
from app.modules.users.models import User


def _elo_delta(rating_self: int, rating_other: int, score_self: float, k: int = 24) -> int:
    expected = 1.0 / (1.0 + (10 ** ((rating_other - rating_self) / 400.0)))
    return int(round(k * (score_self - expected)))


def _average_time_ms(db: Session, session_id: int) -> int:
    return int(
        db.query(func.coalesce(func.avg(Attempt.time_taken_ms), 0))
        .filter(Attempt.session_id == session_id)
        .scalar()
        or 0
    )


def _tempo_bonus(avg_self_ms: int, avg_other_ms: int) -> int:
    if avg_self_ms <= 0 or avg_other_ms <= 0:
        return 0
    diff = avg_other_ms - avg_self_ms
    raw = int(diff / 1800)
    return max(-4, min(4, raw))


def _resolve_outcome(session_self: GameSession, session_other: GameSession) -> float:
    if session_self.total_questions == 0 and session_other.total_questions > 0:
        return 0.0
    if session_other.total_questions == 0 and session_self.total_questions > 0:
        return 1.0

    if session_self.correct_answers > session_other.correct_answers:
        return 1.0
    if session_self.correct_answers < session_other.correct_answers:
        return 0.0

    wrong_self = max(0, int(session_self.total_questions or 0) - int(session_self.correct_answers or 0))
    wrong_other = max(0, int(session_other.total_questions or 0) - int(session_other.correct_answers or 0))
    if wrong_self < wrong_other:
        return 1.0
    if wrong_self > wrong_other:
        return 0.0

    # desempate final por menor tempo medio de resposta.
    times_self = [a.time_taken_ms for a in session_self.attempts] if session_self.attempts else []
    times_other = [a.time_taken_ms for a in session_other.attempts] if session_other.attempts else []
    avg_self = int(sum(times_self) / len(times_self)) if times_self else 0
    avg_other = int(sum(times_other) / len(times_other)) if times_other else 0
    if avg_self > 0 and avg_other > 0:
        if avg_self < avg_other:
            return 1.0
        if avg_self > avg_other:
            return 0.0
    return 0.5


def join_ranked_queue(db: Session, user: User, level: int, locale: str = "en") -> dict:
    store = get_competitive_store()
    pending = store.pop_pending(user.id)
    if pending:
        return pending

    season = get_active_season(db)
    if not season:
        raise HTTPException(status_code=409, detail=t("no_active_season_for_ranked", locale))

    level = get_level_for_points(db, int(user.points or 0))

    if store.is_user_in_queue(user.id):
        raise HTTPException(status_code=409, detail=t("already_in_ranked_queue", locale))

    tolerance = 250
    opponent = store.find_and_pop_opponent(
        rating=int(user.points),
        level=level,
        tolerance=tolerance,
        exclude_user_id=user.id,
    )

    if opponent is None:
        store.enqueue(
            {
                "user_id": int(user.id),
                "username": str(user.username),
                "rating": int(user.points),
                "level": int(level),
                "queued_at": float(time.time()),
            }
        )
        return {
            "status": "waiting",
            "message": t("ranked_waiting_opponent", locale),
            "session_id": None,
            "opponent_username": None,
            "level": level,
        }

    seed = random.randint(1, 2_000_000_000)
    session_self = GameSession(user_id=user.id, season_id=season.id, mode="ranked", level=level, seed=seed)
    session_opp = GameSession(user_id=opponent.user_id, season_id=season.id, mode="ranked", level=level, seed=seed)
    db.add(session_self)
    db.add(session_opp)
    db.commit()
    db.refresh(session_self)
    db.refresh(session_opp)

    state = {
        "match_id": str(uuid.uuid4()),
        "session_a_id": int(session_self.id),
        "session_b_id": int(session_opp.id),
        "user_a_id": int(user.id),
        "user_b_id": int(opponent["user_id"]),
    }
    store.bind_match(session_self.id, session_opp.id, state)
    store.set_pending(
        int(opponent["user_id"]),
        {
            "status": "matched",
            "message": "matched",
            "session_id": session_opp.id,
            "opponent_username": user.username,
            "level": level,
        },
    )

    return {
        "status": "matched",
        "message": "matched",
        "session_id": session_self.id,
        "opponent_username": opponent["username"],
        "level": level,
    }


def ranked_queue_status(user_id: int, locale: str = "en") -> dict:
    pending = get_competitive_store().pop_pending(user_id)
    if pending:
        return pending
    return {
        "status": "waiting",
        "message": t("ranked_waiting_opponent", locale),
        "session_id": None,
        "opponent_username": None,
        "level": None,
    }


def resolve_ranked_session(
    db: Session,
    session_id: int,
    requester_user_id: int | None = None,
    locale: str = "en",
) -> dict:
    store = get_competitive_store()
    state = store.get_match(session_id)
    if not state:
        raise HTTPException(status_code=404, detail=t("no_ranked_match_for_session", locale))

    a = db.query(GameSession).filter(GameSession.id == int(state["session_a_id"])).first()
    b = db.query(GameSession).filter(GameSession.id == int(state["session_b_id"])).first()
    if not a or not b:
        raise HTTPException(status_code=404, detail=t("no_ranked_match_for_session", locale))

    session_self = a if a.id == session_id else b
    session_other = b if a.id == session_id else a
    if requester_user_id is not None and int(requester_user_id) != int(session_self.user_id):
        raise HTTPException(status_code=403, detail=t("forbidden", locale))

    user_self = db.query(User).filter(User.id == session_self.user_id).first()
    user_other = db.query(User).filter(User.id == session_other.user_id).first()
    if not user_self or not user_other:
        raise HTTPException(status_code=404, detail=t("user_not_found", locale))

    if session_self.is_active or session_other.is_active:
        return {
            "status": "pending",
            "detail": t("ranked_waiting_opponent", locale),
            "delta_points": 0,
            "points_after": int(user_self.points),
        }

    if not store.mark_match_rated(str(state["match_id"])):
        return {"status": "resolved", "detail": "already_resolved", "delta_points": 0, "points_after": int(user_self.points)}

    score_self = _resolve_outcome(session_self, session_other)
    score_other = 1.0 - score_self

    delta_self = _elo_delta(int(user_self.points), int(user_other.points), score_self)
    delta_other = _elo_delta(int(user_other.points), int(user_self.points), score_other)
    avg_self = _average_time_ms(db, session_self.id)
    avg_other = _average_time_ms(db, session_other.id)
    tempo_self = _tempo_bonus(avg_self, avg_other)
    tempo_other = -tempo_self

    user_self.points = max(0, int(user_self.points) + delta_self + tempo_self)
    user_other.points = max(0, int(user_other.points) + delta_other + tempo_other)
    db.commit()

    return {
        "status": "resolved",
        "detail": "ok",
        "delta_points": int(delta_self + tempo_self),
        "points_after": int(user_self.points),
    }
