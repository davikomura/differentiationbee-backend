from fastapi import Request

SUPPORTED_LOCALES = {"pt-BR", "en", "es"}

MESSAGES: dict[str, dict[str, str]] = {
    "season_ends_after_start": {
        "pt-BR": "ends_at deve ser maior que starts_at",
        "en": "ends_at must be greater than starts_at",
        "es": "ends_at debe ser mayor que starts_at",
    },
    "season_slug_exists": {
        "pt-BR": "Season com esse slug ja existe",
        "en": "A season with this slug already exists",
        "es": "Ya existe una season con este slug",
    },
    "season_translation_required": {
        "pt-BR": "Informe ao menos uma traducao em translations",
        "en": "Provide at least one translation in translations",
        "es": "Informa al menos una traduccion en translations",
    },
    "season_translation_duplicate": {
        "pt-BR": "Locale duplicado em translations: {locale_value}",
        "en": "Duplicate locale in translations: {locale_value}",
        "es": "Locale duplicado en translations: {locale_value}",
    },
    "season_translation_missing_required": {
        "pt-BR": "Translations devem conter exatamente os locales: pt-BR, en, es. Faltando: {missing}",
        "en": "Translations must contain exactly locales: pt-BR, en, es. Missing: {missing}",
        "es": "Translations deben contener exactamente los locales: pt-BR, en, es. Faltan: {missing}",
    },
    "season_translation_unsupported": {
        "pt-BR": "Locale nao suportado em translations: {locale_value}",
        "en": "Unsupported locale in translations: {locale_value}",
        "es": "Locale no soportado en translations: {locale_value}",
    },
    "active_session_exists": {
        "pt-BR": "Ja existe uma sessao ativa para este usuario",
        "en": "There is already an active session for this user",
        "es": "Ya existe una sesion activa para este usuario",
    },
    "no_active_season": {
        "pt-BR": "Nao existe season ativa no momento",
        "en": "There is no active season right now",
        "es": "No hay season activa en este momento",
    },
    "session_not_found": {
        "pt-BR": "Sessao nao encontrada",
        "en": "Session not found",
        "es": "Sesion no encontrada",
    },
    "session_closed": {
        "pt-BR": "Sessao encerrada",
        "en": "Session is closed",
        "es": "La sesion esta cerrada",
    },
    "user_not_found": {
        "pt-BR": "Usuario nao encontrado",
        "en": "User not found",
        "es": "Usuario no encontrado",
    },
    "invalid_time_taken_ms": {
        "pt-BR": "time_taken_ms invalido",
        "en": "Invalid time_taken_ms",
        "es": "time_taken_ms invalido",
    },
    "question_not_found": {
        "pt-BR": "Questao nao encontrada",
        "en": "Question not found",
        "es": "Pregunta no encontrada",
    },
    "question_already_answered": {
        "pt-BR": "Questao ja foi respondida",
        "en": "Question has already been answered",
        "es": "La pregunta ya fue respondida",
    },
    "question_time_exceeded": {
        "pt-BR": "Tempo excedido para esta questao",
        "en": "Time limit exceeded for this question",
        "es": "Tiempo excedido para esta pregunta",
    },
    "level_range_1_12": {
        "pt-BR": "level deve estar entre 1 e 12",
        "en": "level must be between 1 and 12",
        "es": "level debe estar entre 1 y 12",
    },
    "token_missing_sub": {
        "pt-BR": "Token sem subject (sub)",
        "en": "Token missing subject (sub)",
        "es": "Token sin subject (sub)",
    },
    "token_invalid_sub": {
        "pt-BR": "Token invalido (sub nao e inteiro)",
        "en": "Invalid token (sub is not an integer)",
        "es": "Token invalido (sub no es entero)",
    },
    "token_user_not_found": {
        "pt-BR": "Usuario nao encontrado",
        "en": "User not found",
        "es": "Usuario no encontrado",
    },
    "forbidden": {
        "pt-BR": "Sem permissao",
        "en": "Forbidden",
        "es": "Sin permiso",
    },
    "password_weak": {
        "pt-BR": "Senha fraca. Use ao menos 8 caracteres, uma letra maiuscula e um numero.",
        "en": "Weak password. Use at least 8 characters, one uppercase letter and one number.",
        "es": "Contrasena debil. Usa al menos 8 caracteres, una mayuscula y un numero.",
    },
    "username_invalid": {
        "pt-BR": "Nome de usuario invalido. Use apenas letras minusculas, numeros, '.', '-' ou '_'",
        "en": "Invalid username. Use only lowercase letters, numbers, '.', '-' or '_'",
        "es": "Nombre de usuario invalido. Usa solo letras minusculas, numeros, '.', '-' o '_'",
    },
    "user_or_email_in_use": {
        "pt-BR": "Usuario ou email ja em uso.",
        "en": "Username or email already in use.",
        "es": "Usuario o email ya en uso.",
    },
    "credentials_invalid": {
        "pt-BR": "Credenciais invalidas",
        "en": "Invalid credentials",
        "es": "Credenciales invalidas",
    },
    "refresh_invalid": {
        "pt-BR": "Refresh token invalido",
        "en": "Invalid refresh token",
        "es": "Refresh token invalido",
    },
    "refresh_expired": {
        "pt-BR": "Refresh token expirado",
        "en": "Refresh token expired",
        "es": "Refresh token expirado",
    },
    "token_expired": {
        "pt-BR": "Token expirado",
        "en": "Token expired",
        "es": "Token expirado",
    },
    "token_invalid": {
        "pt-BR": "Token invalido",
        "en": "Invalid token",
        "es": "Token invalido",
    },
    "token_malformed_sub": {
        "pt-BR": "Token malformado (sem sub)",
        "en": "Malformed token (missing sub)",
        "es": "Token malformado (sin sub)",
    },
}


def normalize_locale(locale: str | None) -> str:
    raw = (locale or "en").split(",")[0].strip()
    if raw in SUPPORTED_LOCALES:
        return raw

    base = raw.split("-")[0].lower()
    if base == "pt":
        return "pt-BR"
    if base == "es":
        return "es"
    return "en"


def get_request_locale(request: Request | None) -> str:
    if request is None:
        return "en"
    return normalize_locale(request.headers.get("accept-language"))


def t(key: str, locale: str | None = None, **kwargs) -> str:
    loc = normalize_locale(locale)
    table = MESSAGES.get(key, {})
    template = table.get(loc) or table.get("en") or key
    return template.format(**kwargs)
