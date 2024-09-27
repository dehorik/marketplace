from typing import Type, Annotated
from psycopg2.errors import ForeignKeyViolation
from fastapi import Depends, HTTPException, status

from entities.users.models import UserModel
from auth import PayloadTokenModel, Authorization
from core.database import UserDataBase
from utils import Converter


base_user_dependency = Authorization(min_role_id=1)


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            user_database: Type = UserDataBase
    ):
        self.user_database = user_database


class UserDataGetter(BaseDependency):
    """
    Получение пользовательских данных
    путём валидации access токена из заголовков
    """

    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[
                PayloadTokenModel,
                Depends(base_user_dependency)
            ]
    ) -> UserModel:
        with self.user_database() as user_db:
            user = user_db.read(payload.sub)

        return self.converter.serialization(user)[0]


class RoleUpdater(BaseDependency):
    """Управление ролями пользователей"""

    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, user_id: int, role_id: int) -> UserModel:
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

        return self.converter.serialization(user)[0]


get_user_data_dependency = UserDataGetter()
update_role_dependency = RoleUpdater()
