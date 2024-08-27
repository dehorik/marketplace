from redis import Redis

from utils import Singleton
from core.config_reader import Settings, config


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
    """Класс для сохранения сессий в памяти с помощью redis"""

    def __init__(self, data: ConnectionData = ConnectionData(config)):
        if self.__dict__:
            return

        connection_data = data()

        self.__client = Redis(
            host=connection_data["REDIS_HOST"],
            port=connection_data["REDIS_PORT"],
            decode_responses=True
        )

    def close(self) -> None:
        self.__client.flushall()

    def set(self, session_id: str, user_id: int) -> None:
        self.__client.set(session_id, user_id)

    def get(self, session_id: str) -> str:
        data = self.__client.get(session_id)
        if not data:
            raise ValueError('incorrect session_id')
        else:
            return str(data)

    def delete(self, session_id: str) -> None:
        if self.__client.exists(session_id):
            self.__client.delete(session_id)
        else:
            raise ValueError('incorrect session_id')

    def exists(self, session_id: str) -> bool:
        return self.__client.exists(session_id)
