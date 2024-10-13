from redis import Redis

from auth.exceptions import NonExistentUserError, NonExistentTokenError
from core.settings import Settings, config
from utils import Singleton


class ConnectionData:
    """Класс для извлечения из .env файла конфигурационных данных для redis"""

    def __init__(self, config_redis: Settings = config):
        if type(config_redis) is not Settings:
            raise ValueError("invalid config object type")

        self.__config_redis = config_redis

    def __call__(self) -> dict:
        data = {
            "REDIS_HOST": self.__config_redis.REDIS_HOST,
            "REDIS_PORT": self.__config_redis.REDIS_PORT
        }

        return data


class RedisClient(Singleton):
    """Класс для работы с redis"""

    def __init__(self, data: ConnectionData | dict = ConnectionData()):
        if self.__dict__:
            return

        if type(data) is not dict and type(data) is not ConnectionData:
            raise TypeError("invalid data object")

        if type(data) is ConnectionData:
            data = data()

        try:
            self.__client = Redis(
                host=data["REDIS_HOST"],
                port=data["REDIS_PORT"],
                decode_responses=True
            )
        except KeyError:
            raise ValueError("invalid data object")

    def close(self) -> None:
        # сброс всех данных
        self.__client.flushall()

    def append_token(self, user_id: str | int, token: str) -> None:
        # добавление токена в список (создание списка при отсутствии)
        # максимум сохраненных refresh токенов пользователя - 5

        amount_tokens = self.__client.rpush(user_id, token)

        expire_sec = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        self.__client.expire(str(user_id), expire_sec)

        if amount_tokens >= 6:
            self.__client.lpop(user_id)

    def delete_token(self, user_id: str | int, token: str) -> None:
        # удаление токена из списка токенов пользователя

        if not self.__client.exists(str(user_id)):
            raise NonExistentUserError('user_id does not exist')

        operation = self.__client.lrem(str(user_id), 1, token)

        if not operation:
            raise NonExistentTokenError('token does not exist')

    def get_tokens(self, user_id: str | int) -> list:
        # получение всех токенов пользователя

        if not self.__client.exists(str(user_id)):
            raise NonExistentUserError('user_id does not exist')
        else:
            return self.__client.lrange(user_id, 0, -1)

    def delete_user(self, user_id: str | int) -> None:
        # удаление пользователя и его токенов

        operation = self.__client.delete(str(user_id))

        if not operation:
            raise NonExistentUserError('user_id does not exist')
