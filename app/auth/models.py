from fastapi import Form
from pydantic import BaseModel
from datetime import datetime

from entities.users.models import UserModel


class UserCredentialsModel(BaseModel):
    """Данные для входа/регистрации"""

    user_name: str = Form(min_length=6, max_length=14)
    user_password: str = Form(min_length=8, max_length=18)


class AccessTokenModel(BaseModel):
    access_token: str
    type: str = "Bearer"


class AuthenticationModel(BaseModel):
    """Отдаётся при прохождении аутентификации"""

    user: UserModel
    access_token: AccessTokenModel


class PayloadTokenModel(BaseModel):
    token_type: str
    sub: int
    role_id: int
    iat: datetime | None = None
    exp: datetime | None = None
