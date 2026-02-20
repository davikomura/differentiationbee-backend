from app.core.settings import get_settings


def test_settings_loads_defaults():
    s = get_settings()
    assert s.access_token_expire_minutes > 0
    assert s.refresh_token_expire_days > 0
    assert s.max_refresh_tokens_per_user >= 0
    assert isinstance(s.cors_allow_origins, list)
