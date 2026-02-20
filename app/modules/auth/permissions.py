# app/modules/auth/permissions.py
from fastapi import Depends, HTTPException, status
from app.modules.auth.router import get_current_user
from app.modules.users.models import User

def require_roles(*allowed: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        role = getattr(user, "role", "user")
        if role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão",
            )
        return user
    return _dep