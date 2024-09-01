from psycopg2 import InterfaceError, connect

from core.settings import Settings, config
from utils import Singleton


class ConnectionData:
    """Класс для извлечения из .env файла конфигурационных данных для БД"""

    def __init__(self, config_database: Settings = config):
        if type(config_database) is not Settings:
            raise ValueError("invalid config_database object type")

        self.__config_database = config_database

    def __call__(self) -> dict:
        data = {
            "DATABASE": self.__config_database.DATABASE,
            "DATABASE_USER": self.__config_database.DATABASE_USER,
            "DATABASE_USER_PASSWORD": self.__config_database.DATABASE_USER_PASSWORD,
            "DATABASE_HOST": self.__config_database.DATABASE_HOST,
            "DATABASE_PORT": self.__config_database.DATABASE_PORT
        }

        return data


class Session(Singleton):
    """
    Класс для создания сессий БД и курсоров - ручек,
    с помощью которых производится работа с БД.
    """

    def __init__(self, data: ConnectionData | dict = ConnectionData()):
        if self.__dict__:
            return

        if type(data) is ConnectionData:
            connection_data = data()

            self.__connection = connect(
                dbname=connection_data["DATABASE"],
                user=connection_data["DATABASE_USER"],
                password=connection_data["DATABASE_USER_PASSWORD"],
                host=connection_data["DATABASE_HOST"],
                port=connection_data["DATABASE_PORT"]
            )

        elif type(data) is dict:
            self.__connection = connect(
                dbname=data["DATABASE"],
                user=data["DATABASE_USER"],
                password=data["DATABASE_USER_PASSWORD"],
                host=data["DATABASE_HOST"],
                port=data["DATABASE_PORT"]
            )

        else:
            raise ValueError("invalid database data object")

    def __del__(self):
        try:
            self.close()
        except InterfaceError:
            return

    def close(self) -> None:
        # закрытие подключения к БД (сессии)
        self.__connection.commit()
        self.__connection.close()

    def commit(self) -> None:
        # запись в базу данных
        self.__connection.commit()

    def get_cursor(self):
        # фабрика курсоров
        return self.__connection.cursor()
