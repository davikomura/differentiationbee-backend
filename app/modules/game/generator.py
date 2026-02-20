# app/modules/game/generator.py
import random
import sympy as sp
import uuid

x = sp.Symbol("x")

def generate_random_function(level: int, seed: int = None):
    if seed is not None:
        random.seed(seed)

    def poly_term(degree, coef_range=(1, 5)):
        coef = random.randint(*coef_range)
        return coef * x**degree

    if level == 1:
        expr = poly_term(1) + random.choice([0, poly_term(2)])
    elif level == 2:
        expr = sum([poly_term(i, (-3, 3)) for i in range(1, 4)])
    elif level == 3:
        a, b = random.randint(1, 3), random.randint(1, 3)
        expr = (x - a) * (x + b) * (x + 1)
    elif level == 4:
        func = random.choice([sp.sin, sp.cos, sp.tan])
        expr = func(x) + poly_term(2)
    elif level == 5:
        a = random.randint(1, 3)
        base = random.choice([sp.E, 2])
        inner = poly_term(1) + random.randint(0, 3)
        expr = base ** (a * inner)
    elif level == 6:
        func = random.choice([sp.sin, sp.cos])
        inner = poly_term(2) + random.randint(1, 4)
        expr = x * func(inner)
    elif level == 7:
        f1 = random.choice([sp.sin(x**2), sp.exp(x), sp.log(x**2 + 1)])
        f2 = random.choice([sp.cos(x), x**3 + 2])
        expr = f1 * f2
    elif level == 8:
        numerator = random.choice([x * sp.sin(x), sp.exp(x) + 1])
        denominator = random.choice([sp.cos(x), x**2 + 2])
        expr = numerator / (denominator + sp.Rational(1, 10))
    elif level == 9:
        inner = sp.sin(x**2 + 1) + x**2 + 2
        expr = sp.log(inner) + x * sp.cos(x)
    elif level == 10:
        expr = (x * sp.exp(x)) * sp.sin(x**2 + 1) + sp.log(x**2 + sp.sin(x) + 3)

    elif level == 11:
        a = random.randint(1, 3)
        b = random.randint(1, 4)
        c = random.randint(0, 3)

        d = random.randint(1, 3)
        e = random.randint(0, 4)
        f = random.randint(0, 3)

        exp_inner = a * x**2 + b * x + c
        trig_inner = d * x**2 + e * x + f

        expr = sp.exp(exp_inner) * sp.sin(trig_inner) + poly_term(3, (-2, 2))

    elif level == 12:
        a = random.randint(1, 4)
        b = random.randint(1, 5)
        c = random.randint(1, 3)
        d = random.randint(1, 4)

        numerator = sp.log(x**2 + a * x + b) + x * sp.exp(c * x)
        denominator = sp.sin(x**2 + d) + sp.Rational(11, 10)

        expr = numerator / denominator

    else:
        raise ValueError("Level must be between 1 and 12.")

    derivative = sp.diff(expr, x)

    return {
        "id": str(uuid.uuid4()),
        "expression": expr,
        "derivative": derivative,
        "expression_latex": sp.latex(expr),
        "derivative_latex": sp.latex(derivative),
        "expression_str": str(expr),
        "derivative_str": str(derivative),
        "level": level,
    }