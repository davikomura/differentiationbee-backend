# app/modules/tiers/service.py
from sqlalchemy.orm import Session

from app.modules.tiers.models import Tier, TierTranslation

DEMOTION_GAP = 20

def _normalize_locale(locale: str | None) -> str:
    return (locale or "en").strip()

def _base_lang(locale: str) -> str:
    return locale.split("-")[0]

def _pick_translation(tier: Tier, locale: str) -> TierTranslation | None:
    if not tier.translations:
        return None

    for t in tier.translations:
        if t.locale.lower() == locale.lower():
            return t

    base = _base_lang(locale).lower()
    for t in tier.translations:
        if _base_lang(t.locale).lower() == base:
            return t

    for t in tier.translations:
        if t.locale.lower() == "en":
            return t

    return tier.translations[0]

def _tier_to_read(tier: Tier, locale: str) -> dict:
    tr = _pick_translation(tier, locale)
    title = tr.title if tr else tier.key
    description = tr.description if tr else None
    return {
        "key": tier.key,
        "min_points": tier.min_points,
        "max_points": tier.max_points,
        "title": title,
        "description": description,
    }

def list_tiers_localized(db: Session, locale: str | None) -> list[dict]:
    loc = _normalize_locale(locale)
    tiers = db.query(Tier).order_by(Tier.rank_order.asc()).all()
    return [_tier_to_read(t, loc) for t in tiers]

def get_tier_for_points(db: Session, points: int) -> Tier:
    tiers = db.query(Tier).order_by(Tier.min_points.desc()).all()
    for t in tiers:
        if points >= t.min_points and (t.max_points is None or points <= t.max_points):
            return t
    return db.query(Tier).order_by(Tier.min_points.asc()).first()

def apply_points_change_with_soft_demotion(db: Session, current_points: int, delta: int) -> int:
    new_val = max(0, current_points + delta)
    current_tier = get_tier_for_points(db, current_points)

    if delta < 0 and new_val < current_tier.min_points:
        if new_val >= (current_tier.min_points - DEMOTION_GAP):
            return current_tier.min_points
    return new_val

def tier_to_read(tier: Tier, locale: str) -> dict:
    tr = _pick_translation(tier, locale)
    return {
        "key": tier.key,
        "min_points": tier.min_points,
        "max_points": tier.max_points,
        "title": tr.title if tr else tier.key,
        "description": tr.description if tr else None,
    }

def apply_match_result_with_soft_demotion(
    db: Session,
    current_points: int,
    delta: int,
) -> int:
    new_val = max(0, current_points + delta)

    current_tier = get_tier_for_points(db, current_points)

    if delta < 0 and new_val < current_tier.min_points:
        if new_val >= (current_tier.min_points - DEMOTION_GAP):
            return current_tier.min_points

    return new_val

def season_reset_points(points: int) -> int:
    if points <= 1000:
        return points
    excess = points - 1000
    reduced = int(excess * 0.75)
    return 1000 + reduced