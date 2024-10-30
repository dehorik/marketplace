from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    """Схема данных пользователя"""

    user_id: int
    role_id: int
    username: str = Field(min_length=6, max_length=16)
    email: EmailStr | None = None
    registration_date: datetime
    photo_path: str | None = None


class EmailVerificationRequest(BaseModel):
    token: str


class ChangeRoleRequest(BaseModel):
    user_id: int = Field(ge=1)
    role_id: int = Field(ge=1)


class AdminModel(BaseModel):
    """
    Схема данных пользователя в списке администраторов
    (отправляется в ответе на запрос получения списка суперюзеров и админов)
    """

    user_id: int
    role_id: int
    role_name: str
    username: str = Field(min_length=6, max_length=16)
    photo_path: str | None = None


class AdminListModel(BaseModel):
    admins: List[AdminModel]
