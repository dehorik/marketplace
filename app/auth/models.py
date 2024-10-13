from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    """Схема данных пользователя"""

    user_id: int
    role_id: int
    username: str = Field(min_length=6, max_length=16)
    email: EmailStr | None = None
    photo_path: str | None = None


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
