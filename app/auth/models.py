from pydantic import BaseModel
from datetime import datetime

from entities.users.models import UserModel


class AccessTokenModel(BaseModel):
    access_token: str
    type: str = "Bearer"


class ExtendedUserModel(BaseModel):
    """
    Расширенная схема пользователя.
    Отдаётся после входа в аккаунт или регистрации
    """

    user: UserModel
    token: AccessTokenModel


class PayloadTokenModel(BaseModel):
    """Полезная нагрузка токена"""

    token_type: str
    sub: int
    iat: datetime | None = None
    exp: datetime | None = None
