# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated
from datetime import datetime

UsernameStr = Annotated[str, StringConstraints(min_length=3, max_length=30)]
PasswordStr = Annotated[str, StringConstraints(min_length=6)]

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
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
