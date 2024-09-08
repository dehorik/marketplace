from redis import Redis

from auth.exceptions import (
    InvalidDataObject,
    InvalidUserException,
    InvalidTokenException
)
from core.settings import Settings, config
from utils import Singleton


class ConnectionData:
    """Класс для извлечения из .env файла конфигурационных данных для redis"""

    def __init__(self, config_database: Settings = config):
        self.__config_database = config_database

    def __call__(self) -> dict:
        data = {
            "REDIS_HOST": self.__config_database.REDIS_HOST,
            "REDIS_PORT": self.__config_database.REDIS_PORT
        }

        return data


class RedisClient(Singleton):
    """Класс для работы с redis"""

    def __init__(self, data: ConnectionData | dict = ConnectionData()):
        if self.__dict__:
            return

        if type(data) is not dict and type(data) is not ConnectionData:
            raise InvalidDataObject("invalid database data object")

        if type(data) is ConnectionData:
            data = data()

        try:
            self.__client = Redis(
                host=data["REDIS_HOST"],
                port=data["REDIS_PORT"],
                decode_responses=True
            )
        except KeyError:
            raise InvalidDataObject("invalid database data object")

    def close(self) -> None:
        # сброс всех данных
        self.__client.flushall()

    def append_token(self, user_id: str | int, token: str) -> None:
        # добавление токена в список (создание списка при отсутствии)
        # максимум сохраненных refresh токенов пользователя - 5

        user_id = str(user_id)
        if self.__client.rpush(user_id, token) >= 6:
            self.__client.lpop(user_id)

    def delete_token(self, user_id: str | int, token: str) -> None:
        # удаление токена из списка

        user_id = str(user_id)
        if not self.__client.exists(user_id):
            raise InvalidUserException('user_id does not exist')

        operation = self.__client.lrem(user_id, 1, token)
        if not operation:
            raise InvalidTokenException('token does not exist')

    def get_tokens(self, user_id: str | int) -> list:
        # получение всех токенов пользователя

        user_id = str(user_id)
        if not self.__client.exists(user_id):
            raise InvalidUserException('user_id does not exist')
        else:
            return self.__client.lrange(user_id, 0, -1)

    def delete_user(self, user_id: str | int) -> None:
        # удаление пользователя и его токенов

        user_id = str(user_id)
        operation = self.__client.delete(user_id)
        if not operation:
            raise InvalidUserException('user_id does not exist')
