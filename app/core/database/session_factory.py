import psycopg2

from core.database.singleton import Singleton
from core.config_reader import Settings
from core.config_reader import config


class ConnectorData:
    """
    Класс для извлечения из .env файла конфигурационных данных для БД
    """

    def __init__(self, data: Settings):
        self.__data = data

    def __call__(self) -> dict:
        result = {
            "DATABASE": config.getenv("DATABASE"),
            "DATABASE_USER": config.getenv("DATABASE_USER"),
            "DATABASE_USER_PASSWORD": config.getenv("DATABASE_USER_PASSWORD"),
            "DATABASE_HOST": config.getenv("DATABASE_HOST"),
            "DATABASE_PORT": config.getenv("DATABASE_PORT")
        }
        return result


class BaseSession(Singleton):
    """
    Класс для создания сессий БД и курсоров - ручек,
    с помощью которых производится работа с БД.
    """

    def __init__(self, data: ConnectorData):
        connection_data = data()

        self.__connection = psycopg2.connect(
            dbname=connection_data["DATABASE"],
            user=connection_data["DATABASE_USER"],
            password=connection_data["DATABASE_USER_PASSWORD"],
            host=connection_data["DATABASE_HOST"],
            port=connection_data["DATABASE_PORT"]
        )

    def __del__(self):
        self.__connection.commit()
        self.__connection.close()

    def close_connection(self) -> None:
        self.__connection.commit()
        self.__connection.close()

    def get_cursor(self):
        return self.__connection.cursor()
