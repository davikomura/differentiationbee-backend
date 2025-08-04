# app/services/validator.py
import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.abc import x

def validate_answer(original_expr_str: str, user_input_str: str, time_taken: float, level: int = 1, use_latex: bool = False):
    try:
        if use_latex:
            original_expr = parse_latex(original_expr_str)
            user_expr = parse_latex(user_input_str)
        else:
            original_expr = sp.sympify(original_expr_str)
            user_expr = sp.sympify(user_input_str)

        correct_derivative = sp.diff(original_expr, x)
        is_correct = sp.simplify(correct_derivative - user_expr) == 0

        score = 0
        if is_correct:
            BASE_SCORE = 100
            score = round(BASE_SCORE * level / (time_taken + 1))

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