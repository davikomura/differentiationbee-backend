from app.modules.sessions.service import compute_session_points_delta


def test_points_delta_zero_questions():
    assert compute_session_points_delta(0, 0, 0) == 0


def test_points_delta_respects_limits():
    assert compute_session_points_delta(total_score=100000, total_questions=10, correct_answers=10) <= 60
    assert compute_session_points_delta(total_score=0, total_questions=10, correct_answers=0) >= -80


def test_points_delta_penalizes_errors():
    good = compute_session_points_delta(total_score=500, total_questions=10, correct_answers=9)
    bad = compute_session_points_delta(total_score=500, total_questions=10, correct_answers=2)
    assert good > bad
