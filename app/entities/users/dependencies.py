from typing import Type, Annotated
from fastapi import Depends, HTTPException, Form, status
from psycopg2.errors import ForeignKeyViolation

from entities.users.models import UserModel
from auth import PayloadTokenModel, Authorization
from core.database import UserDataBase
from utils import Converter


base_user_dependency = Authorization(min_role_id=1)
admin_dependency = Authorization(min_role_id=2)
owner_dependency = Authorization(min_role_id=3)


class BaseDependency:
    def __init__(
            self,
            user_database: Type[UserDataBase] = UserDataBase
    ):
        self.user_database = user_database


class UserDataGettingService(BaseDependency):
    """
    Получение пользовательских данных
    путём валидации access токена из заголовков
    """

    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)]
    ) -> UserModel:
        with self.user_database() as user_db:
            user = user_db.read(payload.sub)

        return self.converter(user)[0]


class RoleUpdateService(BaseDependency):
    """Управление ролями пользователей"""

    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(owner_dependency)],
            user_id: Annotated[int, Form(ge=1)],
            role_id: Annotated[int, Form(ge=1)]
    ) -> UserModel:
        if payload.sub == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_CONFLICT,
                detail="you cannot change your role"
            )

        try:
            with self.user_database() as user_db:
                user = user_db.set_role(user_id, role_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect user_id"
                )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect role_id"
            )

        return self.converter(user)[0]


user_data_getting_service = UserDataGettingService()
role_update_service = RoleUpdateService()
