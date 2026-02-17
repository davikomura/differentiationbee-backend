from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.modules.seasons.models import Season, SeasonTranslation
from app.modules.seasons.schemas import SeasonCreate

def _normalize_locale(locale: str | None) -> str:
    return (locale or "en").strip()

def _base_lang(locale: str) -> str:
    return locale.split("-")[0]

def _pick_translation(season: Season, locale: str) -> SeasonTranslation | None:
    if not season.translations:
        return None

    for t in season.translations:
        if t.locale.lower() == locale.lower():
            return t

    base = _base_lang(locale).lower()
    for t in season.translations:
        if _base_lang(t.locale).lower() == base:
            return t

    for t in season.translations:
        if t.locale.lower() == "en":
            return t

    return season.translations[0]

def create_season(db: Session, data: SeasonCreate) -> Season:
    if data.ends_at <= data.starts_at:
        raise HTTPException(status_code=400, detail="ends_at deve ser maior que starts_at")

    exists = db.query(Season).filter(Season.slug == data.slug).first()
    if exists:
        raise HTTPException(status_code=409, detail="Season com esse slug já existe")

    if not data.translations:
        raise HTTPException(status_code=400, detail="Informe ao menos uma tradução em translations")

    s = Season(
        slug=data.slug,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
    )

    seen_locales = set()
    for tr in data.translations:
        key = tr.locale.lower()
        if key in seen_locales:
            raise HTTPException(status_code=400, detail=f"Locale duplicado em translations: {tr.locale}")
        seen_locales.add(key)
        s.translations.append(
            SeasonTranslation(
                locale=tr.locale,
                title=tr.title,
                description=tr.description,
            )
        )

    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def get_active_season(db: Session) -> Season | None:
    now = datetime.now(timezone.utc)
    return (
        db.query(Season)
        .filter(Season.starts_at <= now, Season.ends_at > now)
        .order_by(Season.starts_at.desc())
        .first()
    )

def get_active_season_localized(db: Session, locale: str | None) -> dict | None:
    s = get_active_season(db)
    if not s:
        return None

    loc = _normalize_locale(locale)
    tr = _pick_translation(s, loc)

    title = tr.title if tr else s.slug
    description = tr.description if tr else None

    return {
        "id": s.id,
        "slug": s.slug,
        "starts_at": s.starts_at,
        "ends_at": s.ends_at,
        "title": title,
        "description": description,
    }