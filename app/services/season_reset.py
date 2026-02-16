# app/services/season_reset.py
from __future__ import annotations
import os

SEASON_RESET_BASE = int(os.getenv("SEASON_RESET_BASE") or "100")
SEASON_RESET_FACTOR = float(os.getenv("SEASON_RESET_FACTOR") or "0.76")

def soft_reset_rating(prev_rating: int) -> int:
    base = SEASON_RESET_BASE
    factor = SEASON_RESET_FACTOR
    r = max(0, int(prev_rating))
    if r <= base:
        return base
    v = base + factor * (r - base)
    return max(base, int(round(v)))