from redis import Redis

from auth.exceptions import InvalidUserException, InvalidTokenException
from core.settings import Settings, config
from utils import Singleton


class ConnectionData:
    """Класс для извлечения из .env файла конфигурационных данных для БД redis"""

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

        if type(data) is ConnectionData:
            connection_data = data()

            self.__client = Redis(
                host=connection_data["REDIS_HOST"],
                port=connection_data["REDIS_PORT"],
                decode_responses=True
            )
        elif type(data) is dict:
            self.__client = Redis(
                host=data["REDIS_HOST"],
                port=data["REDIS_PORT"],
                decode_responses=True
            )
        else:
            raise ValueError("invalid database data object")

    def close(self) -> None:
        # сброс всех данных
        self.__client.flushall()

    def push_token(self, user_id: str | int, token: str) -> None:
        # добавление токена в список или создание списка и добавление в него токена
        user_id = str(user_id)
        self.__client.rpush(user_id, token)

    def delete_token(self, user_id: str | int, token: str) -> None:
        # удаление токена из списка токенов пользователя

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
