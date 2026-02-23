from datetime import date

from app.modules.stats.service import _compute_streaks, _safe_accuracy


def test_safe_accuracy_handles_zero_total():
    assert _safe_accuracy(0, 0) == 0.0


def test_safe_accuracy_returns_percentage():
    assert _safe_accuracy(3, 4) == 75.0


def test_compute_streaks_returns_current_and_best():
    days = [
        date(2026, 2, 15),
        date(2026, 2, 16),
        date(2026, 2, 17),
        date(2026, 2, 19),
        date(2026, 2, 20),
    ]
    current, best = _compute_streaks(days, today=date(2026, 2, 20))
    assert current == 2
    assert best == 3


def test_compute_streaks_empty():
    current, best = _compute_streaks([], today=date(2026, 2, 20))
    assert current == 0
    assert best == 0
