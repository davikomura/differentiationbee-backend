# app/services/elo.py
from __future__ import annotations
import random
from dataclasses import dataclass

@dataclass(frozen=True)
class Arena:
    index: int
    name: str
    min_rating: int
    max_rating: int | None
    level_min: int
    level_max: int

ARENAS: list[Arena] = [
    Arena(1, "Vale dos Polinômios", 0, 199, 1, 2),
    Arena(2, "Floresta das Tangentes", 200, 399, 1, 3),
    Arena(3, "Planícies das Cadeias", 400, 649, 2, 4),
    Arena(4, "Torres do Produto", 650, 949, 3, 5),
    Arena(5, "Deserto Logarítmico", 950, 1299, 4, 6),
    Arena(6, "Montanhas da Composição", 1300, 1699, 5, 7),
    Arena(7, "Catedral das Séries", 1700, 2199, 6, 8),
    Arena(8, "Abismo das Identidades", 2200, 2799, 7, 9),
    Arena(9, "Labirinto das Derivadas", 2800, 3499, 8, 10),
    Arena(10, "Trono de Euler", 3500, None, 9, 10),
]

DEFAULT_RATING = 100

def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v

def get_arena_for_rating(rating: int) -> Arena:
    r = max(0, int(rating))
    for a in ARENAS:
        if a.max_rating is None:
            return a
        if a.min_rating <= r <= a.max_rating:
            return a
    return ARENAS[0]

def pick_level_for_arena(arena: Arena) -> int:
    return random.randint(arena.level_min, arena.level_max)

def target_time_for_level(level: int) -> float:
    lvl = max(1, min(10, int(level)))
    return 28.0 - 1.6 * (lvl - 1)

def compute_rating_delta(is_correct: bool, level: int, time_taken: float) -> int:
    base_gain = 15.0
    base_loss = 8.0
    lvl = max(1, min(10, int(level)))
    t = max(0.0, float(time_taken))
    if not is_correct:
        loss = base_loss + 0.8 * max(0, lvl - 6)
        return -int(round(loss))
    target = target_time_for_level(lvl)
    factor = clamp(target / (t + 1.0), 0.6, 1.5)
    gain = base_gain * factor
    gain += 0.6 * max(0, lvl - 5)
    return int(round(gain))

def arena_progress(rating: int, arena: Arena) -> dict:
    r = max(0, int(rating))
    if arena.max_rating is None:
        return {"current": r, "min": arena.min_rating, "max": None, "pct": None}
    span = max(1, arena.max_rating - arena.min_rating + 1)
    pct = clamp((r - arena.min_rating) / span, 0.0, 1.0)
    return {"current": r, "min": arena.min_rating, "max": arena.max_rating, "pct": pct}