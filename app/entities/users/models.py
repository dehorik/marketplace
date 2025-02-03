from typing import List
from datetime import date
from pydantic import BaseModel, Field, EmailStr


class EmailVerificationRequest(BaseModel):
    token: str


class SetRoleRequest(BaseModel):
    user_id: int = Field(ge=1)
    role_id: int = Field(ge=1)


class UserModel(BaseModel):
    """Схема данных пользователя"""

    user_id: int
    role_id: int
    username: str
    email: EmailStr | None
    registration_date: date
    has_photo: bool


class UserItemModel(BaseModel):
    """Схема данных элемента в ответе на запрос на получение пользователей"""

    user_id: int
    role_id: int
    role_name: str
    username: str
    has_photo: bool


class UserItemListModel(BaseModel):
    users: List[UserItemModel]
