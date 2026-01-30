# app/services/validator.py
import sympy as sp
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
from sympy.abc import x

ALLOWED = {
    "x": x,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
    "pi": sp.pi,
    "E": sp.E,
}

def _parse_expr_safe(s: str):
    return parse_expr(
        s,
        local_dict=ALLOWED,
        global_dict={},
        evaluate=True
    )

def validate_answer(
    original_expr_str: str,
    user_input_str: str,
    time_taken: float,
    level: int = 1,
    use_latex: bool = False
):
    try:
        if use_latex:
            original_expr = parse_latex(original_expr_str)
            user_expr = parse_latex(user_input_str)
        else:
            original_expr = _parse_expr_safe(original_expr_str)
            user_expr = _parse_expr_safe(user_input_str)

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