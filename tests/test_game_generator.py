from app.modules.game.generator import generate_random_function


def test_generator_supports_all_levels():
    for level in range(1, 13):
        result = generate_random_function(level=level, seed=100 + level)
        assert result["level"] == level
        assert isinstance(result["expression_str"], str)
        assert isinstance(result["derivative_str"], str)
        assert result["expression_str"]
        assert result["derivative_str"]
