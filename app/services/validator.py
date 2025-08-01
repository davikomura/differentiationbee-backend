import sympy as sp

x = sp.Symbol('x')

def validate_answer(original_expr_str: str, user_input_str: str, time_taken: float):
    try:
        original_expr = sp.sympify(original_expr_str)
        user_expr = sp.sympify(user_input_str)
        correct_derivative = sp.diff(original_expr, x)

        is_correct = sp.simplify(correct_derivative - user_expr) == 0

        score = 0
        if is_correct:
            score = round(1000 / (time_taken + 1))

        return {
            "is_correct": is_correct,
            "correct_derivative_latex": sp.latex(correct_derivative),
            "score": score
        }

    except Exception as e:
        return {
            "is_correct": False,
            "error": str(e),
            "score": 0
        }