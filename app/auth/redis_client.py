from redis import Redis

from core.config_reader import Settings, config
from core.database.singleton import Singleton


class ConnectionData:
    """Класс для извлечения из .env файла конфигурационных данных для БД redis"""

    def __init__(self, config_database: Settings):
        self.__config_database = config_database

    def __call__(self) -> dict:
        data = {
            "REDIS_HOST": self.__config_database.getenv("REDIS_HOST"),
            "REDIS_PORT": self.__config_database.getenv("REDIS_PORT")
        }

        return data


class RedisClient(Singleton):
    def __init__(self, data: ConnectionData = ConnectionData(config)):
        if self.__dict__:
            return

        connection_data = data()

        self.__client = Redis(
            host=connection_data["REDIS_HOST"],
            port=connection_data["REDIS_PORT"],
            decode_responses=True
        )

    def set(self, key: str, value: str) -> None:
        self.__client.set(key, value)

    def get(self, key: str) -> str:
        return self.__client.get(key)

    def delete(self, key: str) -> None:
        pass

