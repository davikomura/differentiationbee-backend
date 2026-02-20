# app/modules/users/roles.py
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"