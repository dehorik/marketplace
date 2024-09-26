from typing import Type, Annotated
from fastapi import Depends

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


class GetUserDataDependency(BaseDependency):
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


get_user_data_dependency = GetUserDataDependency()
