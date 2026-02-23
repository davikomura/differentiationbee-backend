from app.modules.game.time_limits import get_time_limit_ms


def test_time_limits_low_levels():
    assert get_time_limit_ms(1) == 35_000
    assert get_time_limit_ms(2) == 45_000
    assert get_time_limit_ms(3) == 45_000


def test_time_limits_mid_and_high_levels():
    assert get_time_limit_ms(4) == 55_000
    assert get_time_limit_ms(5) == 55_000
    assert get_time_limit_ms(6) == 60_000
    assert get_time_limit_ms(8) == 60_000
    assert get_time_limit_ms(9) == 75_000
    assert get_time_limit_ms(11) == 90_000
    assert get_time_limit_ms(12) == 105_000


def test_time_limits_default_for_invalid_level():
    assert get_time_limit_ms(0) == 35_000
    assert get_time_limit_ms(99) == 60_000
