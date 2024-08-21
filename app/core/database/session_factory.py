from psycopg2 import InterfaceError, connect

from core.database.singleton import Singleton
from core.config_reader import Settings
from core.config_reader import config


class ConnectionData:
    """Класс для извлечения из .env файла конфигурационных данных для БД"""

    def __init__(self, data: Settings):
        self.__data = data

    def __call__(self) -> dict:
        data = {
            "DATABASE": config.getenv("DATABASE"),
            "DATABASE_USER": config.getenv("DATABASE_USER"),
            "DATABASE_USER_PASSWORD": config.getenv("DATABASE_USER_PASSWORD"),
            "DATABASE_HOST": config.getenv("DATABASE_HOST"),
            "DATABASE_PORT": config.getenv("DATABASE_PORT")
        }
        return data


class Session(Singleton):
    """
    Класс для создания сессий БД и курсоров - ручек,
    с помощью которых производится работа с БД.
    """

    def __init__(self, data: ConnectionData = ConnectionData(config)):
        connection_data = data()

        self.__connection = connect(
            dbname=connection_data["DATABASE"],
            user=connection_data["DATABASE_USER"],
            password=connection_data["DATABASE_USER_PASSWORD"],
            host=connection_data["DATABASE_HOST"],
            port=connection_data["DATABASE_PORT"]
        )

    def __del__(self):
        try:
            self.close_connection()
        except InterfaceError:
            pass

    def close_connection(self) -> None:
        self.__connection.commit()
        self.__connection.close()

    def commit(self) -> None:
        self.__connection.commit()

    def get_cursor(self):
        # фабрика курсоров

        return self.__connection.cursor()
