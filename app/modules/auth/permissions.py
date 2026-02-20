from fastapi import Depends, HTTPException, Request, status

from app.core.i18n import get_request_locale, t
from app.modules.auth.router import get_current_user
from app.modules.users.models import User


def require_roles(*allowed: str):
    def _dep(request: Request, user: User = Depends(get_current_user)) -> User:
        role = getattr(user, "role", "user")
        if role not in allowed:
            locale = get_request_locale(request)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=t("forbidden", locale),
            )
        return user

    return _dep
