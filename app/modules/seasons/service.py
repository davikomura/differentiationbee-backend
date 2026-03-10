from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.i18n import SUPPORTED_LOCALES, t
from app.modules.seasons.models import Season, SeasonTranslation
from app.modules.seasons.schemas import SeasonCreate


def _normalize_locale(locale: str | None) -> str:
    return (locale or "en").strip()


def _base_lang(locale: str) -> str:
    return locale.split("-")[0]


def _pick_translation(season: Season, locale: str) -> SeasonTranslation | None:
    if not season.translations:
        return None

    for tr in season.translations:
        if tr.locale.lower() == locale.lower():
            return tr

    base = _base_lang(locale).lower()
    for tr in season.translations:
        if _base_lang(tr.locale).lower() == base:
            return tr

    for tr in season.translations:
        if tr.locale.lower() == "en":
            return tr

    return season.translations[0]


def _season_to_read_dict(s: Season, locale: str | None) -> dict:
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


def _normalized_translation_rows(data: SeasonCreate, locale: str | None) -> list[tuple[str, str, str | None]]:
    if not data.translations:
        raise HTTPException(status_code=400, detail=t("season_translation_required", locale))

    required_locales = set(SUPPORTED_LOCALES)
    incoming_locales: set[str] = set()
    rows: list[tuple[str, str, str | None]] = []

    for tr in data.translations:
        normalized = tr.locale.strip()
        if normalized not in SUPPORTED_LOCALES:
            raise HTTPException(status_code=400, detail=t("season_translation_unsupported", locale, locale_value=normalized))
        if normalized in incoming_locales:
            raise HTTPException(status_code=400, detail=t("season_translation_duplicate", locale, locale_value=normalized))
        incoming_locales.add(normalized)
        rows.append((normalized, tr.title, tr.description))

    missing = sorted(required_locales - incoming_locales)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=t("season_translation_missing_required", locale, missing=", ".join(missing)),
        )

    return sorted(rows)


def _season_translation_rows(season: Season) -> list[tuple[str, str, str | None]]:
    return sorted((tr.locale, tr.title, tr.description) for tr in season.translations)


def _is_same_create_payload(season: Season, data: SeasonCreate, translation_rows: list[tuple[str, str, str | None]]) -> bool:
    return (
        season.slug == data.slug
        and _season_translation_rows(season) == translation_rows
    )


def _find_exact_window(db: Session, data: SeasonCreate) -> Season | None:
    return (
        db.query(Season)
        .filter(Season.starts_at == data.starts_at, Season.ends_at == data.ends_at)
        .first()
    )


def _find_overlapping_season(db: Session, data: SeasonCreate) -> Season | None:
    return (
        db.query(Season)
        .filter(Season.starts_at < data.ends_at, Season.ends_at > data.starts_at)
        .first()
    )


def create_season(db: Session, data: SeasonCreate, locale: str | None = None) -> dict:
    if data.ends_at <= data.starts_at:
        raise HTTPException(status_code=400, detail=t("season_ends_after_start", locale))

    translation_rows = _normalized_translation_rows(data, locale)

    exact_window = _find_exact_window(db, data)
    if exact_window:
        if _is_same_create_payload(exact_window, data, translation_rows):
            return _season_to_read_dict(exact_window, locale)
        raise HTTPException(status_code=409, detail=t("season_window_exists", locale))

    exists = db.query(Season).filter(Season.slug == data.slug).first()
    if exists:
        raise HTTPException(status_code=409, detail=t("season_slug_exists", locale))

    overlapping = _find_overlapping_season(db, data)
    if overlapping:
        raise HTTPException(status_code=409, detail=t("season_window_overlap", locale))

    s = Season(
        slug=data.slug,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
    )

    for normalized, title, description in translation_rows:
        s.translations.append(
            SeasonTranslation(
                locale=normalized,
                title=title,
                description=description,
            )
        )

    db.add(s)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        exact_window = _find_exact_window(db, data)
        if exact_window:
            if _is_same_create_payload(exact_window, data, translation_rows):
                return _season_to_read_dict(exact_window, locale)
            raise HTTPException(status_code=409, detail=t("season_window_exists", locale))

        exists = db.query(Season).filter(Season.slug == data.slug).first()
        if exists:
            raise HTTPException(status_code=409, detail=t("season_slug_exists", locale))
        raise

    db.refresh(s)

    return _season_to_read_dict(s, locale)


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
