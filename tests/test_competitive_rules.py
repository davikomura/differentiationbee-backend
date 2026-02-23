from app.modules.attempts.service import _apply_diminishing_returns
from app.modules.competitive.service import _elo_delta, _tempo_bonus


def test_diminishing_returns_low_level():
    assert _apply_diminishing_returns(100, 2) == 65


def test_diminishing_returns_mid_level():
    assert _apply_diminishing_returns(100, 5) == 85


def test_diminishing_returns_high_level():
    assert _apply_diminishing_returns(100, 9) == 100


def test_elo_delta_winner_positive():
    delta = _elo_delta(1200, 1200, 1.0)
    assert delta > 0


def test_elo_delta_loser_negative():
    delta = _elo_delta(1200, 1200, 0.0)
    assert delta < 0


def test_tempo_bonus_rewards_faster_player():
    assert _tempo_bonus(12000, 20000) > 0
    assert _tempo_bonus(22000, 14000) < 0
