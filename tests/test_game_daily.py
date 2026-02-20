from datetime import datetime, timezone

from app.modules.game.service import get_daily_challenge


def test_daily_challenge_is_deterministic_per_day():
    now = datetime(2026, 2, 20, 10, 30, tzinfo=timezone.utc)
    one = get_daily_challenge(now)
    two = get_daily_challenge(now)
    assert one == two


def test_daily_challenge_level_range():
    now = datetime(2026, 2, 20, 10, 30, tzinfo=timezone.utc)
    result = get_daily_challenge(now)
    assert 1 <= result["level"] <= 12
