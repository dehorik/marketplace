from datetime import datetime, date
from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    """Схема данных пользователя"""

    user_id: int
    role_id: int
    username: str
    email: EmailStr | None
    registration_date: date
    photo_path: str | None


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


class TokenPayloadModel(BaseModel):
    """Полезная нагрузка токена"""

    token_type: str
    sub: int
    iat: datetime
    exp: datetime
