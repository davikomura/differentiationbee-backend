from app.modules.sessions.service import compute_session_points_delta, compute_speed_bonus_points


def test_points_delta_zero_questions():
    assert compute_session_points_delta(total_questions=0, correct_answers=0, level=1, avg_time_ms=0) == 0


def test_points_delta_respects_limits():
    assert compute_session_points_delta(total_questions=30, correct_answers=30, level=12, avg_time_ms=1000) <= 100
    assert compute_session_points_delta(total_questions=30, correct_answers=0, level=12, avg_time_ms=999999) >= -100


def test_points_delta_penalizes_errors():
    good = compute_session_points_delta(total_questions=10, correct_answers=9, level=6, avg_time_ms=25000)
    bad = compute_session_points_delta(total_questions=10, correct_answers=2, level=6, avg_time_ms=25000)
    assert good > bad


def test_speed_bonus_rewards_faster():
    fast = compute_speed_bonus_points(12000, level=6)
    slow = compute_speed_bonus_points(50000, level=6)
    assert fast > slow
