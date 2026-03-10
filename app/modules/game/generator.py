# app/modules/game/generator.py
import random
import uuid

import sympy as sp

x = sp.Symbol("x")

def _rand_nonzero(rng: random.Random, low: int, high: int) -> int:
    value = 0
    while value == 0:
        value = rng.randint(low, high)
    return value


def _rand_constant(rng: random.Random, low: int, high: int) -> int:
    return rng.randint(low, high)


def _rand_affine(rng: random.Random, coef_range: tuple[int, int], const_range: tuple[int, int]) -> sp.Expr:
    a = _rand_nonzero(rng, *coef_range)
    b = _rand_constant(rng, *const_range)
    return a * x + b


def _rand_poly(
    rng: random.Random,
    degree: int,
    coef_range: tuple[int, int],
    *,
    min_terms: int = 2,
    include_constant: bool = True,
) -> sp.Expr:
    available_degrees = list(range(degree, -1 if include_constant else 0, -1))
    rng.shuffle(available_degrees)

    chosen = {degree}
    target_terms = min(len(available_degrees), rng.randint(min_terms, len(available_degrees)))
    for deg in available_degrees:
        if len(chosen) >= target_terms:
            break
        chosen.add(deg)

    expr = sp.Integer(0)
    for deg in sorted(chosen, reverse=True):
        coef = _rand_nonzero(rng, *coef_range)
        expr += coef * x**deg
    return sp.expand(expr)


def _rand_positive_quadratic(rng: random.Random, coef_range: tuple[int, int], offset_range: tuple[int, int]) -> sp.Expr:
    a = _rand_nonzero(rng, *coef_range)
    b = _rand_constant(rng, *coef_range)
    c = _rand_constant(rng, *offset_range)
    return x**2 + a * x + b + c


def _build_level_1(rng: random.Random) -> sp.Expr:
    return sp.expand(
        _rand_nonzero(rng, -10, 10) * x**2
        + _rand_nonzero(rng, -15, 15) * x
    )


def _build_level_2(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: _rand_poly(rng, degree=3, coef_range=(-9, 9), min_terms=2, include_constant=False),
        lambda: _rand_poly(rng, degree=3, coef_range=(-12, 12), min_terms=3, include_constant=False),
        lambda: _rand_nonzero(rng, -6, 6) * x**3 + _rand_nonzero(rng, -8, 8) * x**2 + _rand_nonzero(rng, -10, 10) * x,
        lambda: _rand_nonzero(rng, -5, 5) * x**4 + _rand_nonzero(rng, -6, 6) * x**2 + _rand_nonzero(rng, -10, 10) * x,
    ]
    return sp.expand(rng.choice(templates)())


def _build_level_3(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: sp.expand(_rand_affine(rng, (-8, 8), (-10, 10)) * _rand_affine(rng, (-8, 8), (-10, 10))),
        lambda: sp.expand((x + _rand_constant(rng, -8, 8)) * _rand_poly(rng, degree=2, coef_range=(-6, 6), min_terms=2)),
        lambda: sp.expand((_rand_nonzero(rng, -5, 5) * x**2 + _rand_nonzero(rng, -8, 8)) * _rand_affine(rng, (-6, 6), (-8, 8))),
    ]
    return rng.choice(templates)()


def _build_level_4(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: _rand_affine(rng, (-8, 8), (-10, 10)) / _rand_affine(rng, (-8, 8), (-10, 10)),
        lambda: (_rand_poly(rng, degree=2, coef_range=(-6, 6), min_terms=2) + _rand_constant(rng, 1, 5)) / (x + _rand_nonzero(rng, -8, 8)),
        lambda: (_rand_nonzero(rng, -6, 6) * x**2 + _rand_nonzero(rng, -8, 8) * x + _rand_constant(rng, -6, 6)) / _rand_positive_quadratic(rng, (-4, 4), (4, 9)),
    ]
    return sp.together(rng.choice(templates)())


def _build_level_5(rng: random.Random) -> sp.Expr:
    affine = _rand_affine(rng, (-12, 12), (-15, 15))
    quadratic = (
        _rand_nonzero(rng, -6, 6) * x**2
        + _rand_nonzero(rng, -10, 10) * x
        + _rand_constant(rng, -12, 12)
    )
    templates = [
        lambda: sp.sin(affine),
        lambda: sp.cos(affine),
        lambda: sp.tan(affine),
        lambda: sp.sin(quadratic),
        lambda: sp.cos(quadratic),
        lambda: sp.tan(quadratic),
        lambda: sp.sin(affine) + _rand_nonzero(rng, -8, 8) * x,
        lambda: sp.cos(affine) + _rand_nonzero(rng, -6, 6) * x**2,
        lambda: sp.sin(quadratic) + _rand_nonzero(rng, -5, 5) * x,
        lambda: sp.cos(quadratic) + _rand_nonzero(rng, -4, 4) * x**2,
    ]
    return sp.expand_trig(rng.choice(templates)())


def _build_level_6(rng: random.Random) -> sp.Expr:
    affine = _rand_affine(rng, (-10, 10), (-12, 12))
    quadratic = (
        _rand_nonzero(rng, -5, 5) * x**2
        + _rand_nonzero(rng, -8, 8) * x
        + _rand_constant(rng, -10, 10)
    )
    templates = [
        lambda: sp.exp(affine),
        lambda: sp.exp(quadratic),
        lambda: sp.Integer(rng.choice([2, 3, 5, 7])) ** affine,
        lambda: sp.Integer(rng.choice([2, 3, 5])) ** quadratic,
        lambda: sp.log(x**2 + _rand_nonzero(rng, -8, 8) * x + _rand_constant(rng, 8, 18)),
        lambda: sp.log(_rand_positive_quadratic(rng, (-8, 8), (8, 16))),
        lambda: sp.exp(affine) + _rand_nonzero(rng, -8, 8) * x,
        lambda: sp.exp(quadratic) + _rand_nonzero(rng, -6, 6) * x,
        lambda: sp.log(_rand_positive_quadratic(rng, (-8, 8), (8, 16))) + _rand_nonzero(rng, -6, 6) * x,
    ]
    return rng.choice(templates)()


def _build_level_7(rng: random.Random) -> sp.Expr:
    poly = _rand_poly(rng, degree=2, coef_range=(-6, 6), min_terms=2)
    templates = [
        lambda: sp.expand((x + _rand_constant(rng, -6, 6)) * sp.sin(_rand_affine(rng, (-5, 5), (-6, 6)))),
        lambda: sp.expand(poly * sp.cos(x + _rand_constant(rng, -5, 5))),
        lambda: (_rand_affine(rng, (-5, 5), (-6, 6))) * sp.exp(_rand_affine(rng, (-4, 4), (-5, 5))),
        lambda: (x + _rand_constant(rng, 1, 6)) * sp.log(x**2 + _rand_constant(rng, 4, 10)),
    ]
    return rng.choice(templates)()


def _build_level_8(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: sp.sin(_rand_nonzero(rng, -8, 8) * x**2 + _rand_nonzero(rng, -10, 10) * x + _rand_constant(rng, -12, 12)),
        lambda: sp.cos(_rand_nonzero(rng, -6, 6) * x**3 + _rand_nonzero(rng, -8, 8) * x**2 + _rand_nonzero(rng, -10, 10) * x),
        lambda: sp.tan(_rand_nonzero(rng, -6, 6) * x**2 + _rand_nonzero(rng, -8, 8) * x + _rand_constant(rng, -10, 10)),
        lambda: sp.exp(_rand_nonzero(rng, -6, 6) * x**2 + _rand_nonzero(rng, -8, 8) * x + _rand_constant(rng, -10, 10)),
        lambda: sp.exp(_rand_nonzero(rng, -5, 5) * x**3 + _rand_nonzero(rng, -6, 6) * x),
        lambda: sp.log(x**3 + _rand_nonzero(rng, -6, 6) * x**2 + _rand_nonzero(rng, -8, 8) * x + _rand_constant(rng, 8, 18)),
        lambda: sp.log(x**4 + _rand_nonzero(rng, -5, 5) * x**2 + _rand_constant(rng, 10, 18)),
    ]
    return rng.choice(templates)()


def _build_level_9(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: sp.sin(_rand_affine(rng, (-5, 5), (-6, 6))) / _rand_positive_quadratic(rng, (-4, 4), (5, 10)),
        lambda: (sp.exp(_rand_affine(rng, (-4, 4), (-5, 5))) + _rand_affine(rng, (-5, 5), (-6, 6))) / (x + _rand_nonzero(rng, -8, 8)),
        lambda: sp.log(x**2 + _rand_constant(rng, 5, 12)) / _rand_affine(rng, (-5, 5), (-8, 8)),
        lambda: (_rand_poly(rng, degree=2, coef_range=(-5, 5), min_terms=2) * sp.cos(x)) / (x**2 + _rand_constant(rng, 4, 9)),
    ]
    return sp.together(rng.choice(templates)())


def _build_level_10(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: (_rand_nonzero(rng, -5, 5) * x**2 + _rand_constant(rng, 1, 8)) * sp.sin(_rand_affine(rng, (-5, 5), (-5, 5))),
        lambda: (x + _rand_constant(rng, -5, 5)) * sp.exp(_rand_nonzero(rng, -4, 4) * x**2 + _rand_nonzero(rng, -4, 4)),
        lambda: sp.log(x**2 + _rand_constant(rng, 4, 10)) * sp.cos(_rand_affine(rng, (-4, 4), (-5, 5))),
        lambda: (_rand_affine(rng, (-5, 5), (-6, 6))) * sp.exp(x) * sp.sin(x + _rand_constant(rng, -5, 5)),
    ]
    return rng.choice(templates)()


def _build_level_11(rng: random.Random) -> sp.Expr:
    templates = [
        lambda: sp.exp(sp.sin(_rand_affine(rng, (-8, 8), (-10, 10)))),
        lambda: sp.exp(sp.cos(_rand_nonzero(rng, -5, 5) * x**2 + _rand_nonzero(rng, -8, 8) * x + _rand_constant(rng, -10, 10))),
        lambda: sp.log(x**2 + sp.sin(_rand_affine(rng, (-8, 8), (-8, 8))) + _rand_constant(rng, 8, 16)),
        lambda: sp.log(x**2 + sp.cos(_rand_nonzero(rng, -6, 6) * x + _rand_constant(rng, -8, 8)) + _rand_constant(rng, 8, 16)),
        lambda: sp.sin(sp.exp(_rand_affine(rng, (-6, 6), (-8, 8))) + _rand_nonzero(rng, -6, 6) * x**2),
        lambda: sp.cos(sp.exp(_rand_nonzero(rng, -5, 5) * x**2 + _rand_nonzero(rng, -6, 6) * x + _rand_constant(rng, -8, 8))),
        lambda: sp.cos(sp.log(x**2 + _rand_constant(rng, 8, 16))) * sp.exp(_rand_affine(rng, (-6, 6), (-8, 8))),
        lambda: sp.sin(sp.log(x**2 + _rand_constant(rng, 8, 16))) * sp.exp(_rand_nonzero(rng, -5, 5) * x + _rand_constant(rng, -6, 6)),
    ]
    return rng.choice(templates)()


def _build_level_12(rng: random.Random) -> sp.Expr:
    numerator = rng.choice(
        [
            lambda: sp.log(x**2 + _rand_nonzero(rng, -4, 4) * x + _rand_constant(rng, 6, 12)) + x * sp.exp(_rand_affine(rng, (-3, 3), (-4, 4))),
            lambda: (_rand_nonzero(rng, -4, 4) * x**2 + _rand_constant(rng, 2, 8)) * sp.sin(_rand_affine(rng, (-4, 4), (-4, 4))) + sp.log(x**2 + _rand_constant(rng, 5, 11)),
        ]
    )()
    denominator = rng.choice(
        [
            lambda: sp.sin(x**2 + _rand_constant(rng, 2, 8)) + sp.Rational(rng.randint(11, 17), 10),
            lambda: sp.cos(_rand_affine(rng, (-3, 3), (-4, 4))) + x**2 + _rand_constant(rng, 3, 8),
            lambda: sp.exp(_rand_affine(rng, (-2, 2), (-3, 3))) + x**2 + _rand_constant(rng, 2, 6),
        ]
    )()
    return sp.together(numerator / denominator)


LEVEL_BUILDERS = {
    1: _build_level_1,
    2: _build_level_2,
    3: _build_level_3,
    4: _build_level_4,
    5: _build_level_5,
    6: _build_level_6,
    7: _build_level_7,
    8: _build_level_8,
    9: _build_level_9,
    10: _build_level_10,
    11: _build_level_11,
    12: _build_level_12,
}


def generate_random_function(level: int, seed: int = None):
    builder = LEVEL_BUILDERS.get(level)
    if builder is None:
        raise ValueError("Level must be between 1 and 12.")

    rng = random.Random(seed)
    expr = sp.simplify(builder(rng))
    derivative = sp.simplify(sp.diff(expr, x))

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
