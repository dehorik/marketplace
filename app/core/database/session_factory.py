from psycopg2 import InterfaceError, connect
from psycopg2.extensions import cursor

from core.settings import config
from utils import Singleton


class Session(Singleton):
    """Класс для создания сессии базы данных"""

    def __init__(
            self,
            db_name: str,
            user: str,
            password: str,
            host: str,
            port: int
    ):
        if self.__dict__:
            return

        self.__connection = connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.__connection.autocommit = True

    def close(self) -> None:
        # закрытие подключения к базе данных (сессии)
        self.__connection.close()

    def get_cursor(self) -> cursor:
        # фабрика курсоров
        return self.__connection.cursor()


def get_session() -> Session:
    return Session(
        config.DATABASE_NAME,
        config.DATABASE_USER,
        config.DATABASE_USER_PASSWORD,
        config.DATABASE_HOST,
        config.DATABASE_PORT
    )
