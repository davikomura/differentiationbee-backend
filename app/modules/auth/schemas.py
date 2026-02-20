# app/modules/auth/schemas.py
from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated
from datetime import datetime

from app.modules.users.roles import UserRole

UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=30)]
PasswordStr = Annotated[str, StringConstraints(min_length=8)]

class UserCreate(BaseModel):
    username: UsernameStr
    email: EmailStr
    password: PasswordStr

class UserLogin(BaseModel):
    username: UsernameStr
    password: PasswordStr

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str