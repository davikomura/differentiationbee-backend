from app.modules.game.time_limits import get_time_limit_ms


def test_time_limits_low_levels():
    assert get_time_limit_ms(1) == 40_000
    assert get_time_limit_ms(2) == 50_000
    assert get_time_limit_ms(3) == 60_000


def test_time_limits_mid_and_high_levels():
    assert get_time_limit_ms(4) == 70_000
    assert get_time_limit_ms(5) == 80_000
    assert get_time_limit_ms(6) == 90_000
    assert get_time_limit_ms(8) == 110_000
    assert get_time_limit_ms(9) == 125_000
    assert get_time_limit_ms(10) == 140_000
    assert get_time_limit_ms(11) == 160_000
    assert get_time_limit_ms(12) == 180_000


def test_time_limits_default_for_invalid_level():
    assert get_time_limit_ms(0) == 40_000
    assert get_time_limit_ms(99) == 60_000
