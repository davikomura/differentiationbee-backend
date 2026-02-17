# app/modules/game/validator.py
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
        global_dict={"Integer": sp.Integer, "Symbol": sp.Symbol},
        evaluate=True,
    )

def _parse_latex_safe(s: str):
    expr = parse_latex(s)
    return sp.sympify(expr)

def validate_answer(
    correct_derivative_str: str,
    user_input_str: str,
    time_taken: float,
    level: int = 1,
    use_latex: bool = False,
):
    try:
        correct_expr = _parse_expr_safe(correct_derivative_str)

        if use_latex:
            user_expr = _parse_latex_safe(user_input_str)
        else:
            user_expr = _parse_expr_safe(user_input_str)

        is_correct = sp.simplify(correct_expr - user_expr) == 0

        score = 0
        if is_correct:
            BASE_SCORE = 100
            score = round(BASE_SCORE * level / (time_taken + 1))

        return {
            "is_correct": bool(is_correct),
            "correct_derivative_latex": sp.latex(correct_expr),
            "score": int(score),
        }
    except Exception as e:
        return {
            "is_correct": False,
            "error": str(e),
            "score": 0,
        }