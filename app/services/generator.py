import random
import sympy as sp
import uuid

x = sp.Symbol('x')

def generate_random_function(level: int):
    expr = None

    if level == 1:
        n = random.randint(1, 3)
        expr = x**n

    elif level == 2:
        expr = random.randint(1, 5) * x + random.randint(1, 5) * x**2

    elif level == 3:
        expr = random.randint(1, 5)*x + random.randint(1, 5)*x**2 + random.randint(1, 3)*x**3

    elif level == 4:
        func = random.choice([sp.sin, sp.cos, sp.tan])
        expr = func(x)

    elif level == 5:
        a = random.randint(1, 3)
        base = random.choice([sp.E, 2])
        expr = base**(a * x)

    elif level == 6:
        func = random.choice([sp.sin, sp.cos])
        inner = random.randint(1, 5) * x + random.randint(0, 3)
        expr = func(inner)

    elif level == 7:
        f1 = random.choice([x, sp.exp(x), sp.sin(x)])
        f2 = random.choice([x**2, sp.cos(x), sp.exp(x)])
        expr = f1 * f2

    elif level == 8:
        numerator = random.choice([x, sp.exp(x), sp.sin(x)])
        denominator = random.choice([x + 1, sp.cos(x), x**2 + 1])
        expr = numerator / denominator

    elif level == 9:
        inner = random.choice([x**2 + 1, sp.exp(x), sp.sin(x)])
        expr = sp.log(inner)

    elif level == 10:
        expr = x * sp.exp(x) * sp.sin(x) + sp.log(x**2 + 1)

    else:
        raise ValueError("Level must be between 1 and 10.")

    derivative = sp.diff(expr, x)

    return {
        "id": str(uuid.uuid4()),
        "expression": expr,
        "derivative": derivative,
        "expression_latex": sp.latex(expr),
        "expression_str": str(expr),
    }
