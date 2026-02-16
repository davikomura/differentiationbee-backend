# app/services/validator.py
import random
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

def _parse_expr_safe(s: str, evaluate: bool = True):
    return parse_expr(
        s,
        local_dict=ALLOWED,
        global_dict={},
        evaluate=evaluate,
    )

def _safe_numeric_equivalence(expr_a: sp.Expr, expr_b: sp.Expr, attempts: int = 12, samples: int = 8) -> bool:
    diff = sp.simplify(expr_a - expr_b)
    if diff == 0:
        return True

    f = sp.lambdify(x, diff, "math")
    ok = 0
    for _ in range(attempts):
        val = random.uniform(-3.0, 3.0)
        try:
            y = f(val)
            if not (y is None) and abs(float(y)) < 1e-6:
                ok += 1
        except Exception:
            continue
        if ok >= samples:
            return True
    return False

def validate_answer(
    correct_derivative_str: str,
    user_input_str: str,
    time_taken: float,
    level: int,
    use_latex: bool = False,
):
    try:
        if use_latex:
            user_expr = parse_latex(user_input_str)
        else:
            user_expr = _parse_expr_safe(user_input_str, evaluate=False)

        correct_expr = _parse_expr_safe(correct_derivative_str, evaluate=True)

        symbolic_ok = sp.simplify(correct_expr - user_expr) == 0
        is_correct = bool(symbolic_ok) or _safe_numeric_equivalence(correct_expr, user_expr)

        score = 0
        if is_correct:
            base = 100
            score = round(base * level / (time_taken + 1.0))

        return {
            "is_correct": is_correct,
            "correct_derivative_latex": sp.latex(correct_expr),
            "score": int(score),
        }
    except Exception as e:
        return {
            "is_correct": False,
            "error": str(e),
            "score": 0,
        }