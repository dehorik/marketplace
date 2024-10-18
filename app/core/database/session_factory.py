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
            port: int,
            autocommit: bool = True
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
        self.__connection.autocommit = autocommit

    @property
    def autocommit(self) -> bool:
        return self.__connection.autocommit

    @autocommit.setter
    def autocommit(self, value: bool) -> None:
        self.__connection.autocommit = value

    def __del__(self):
        try:
            self.close()
        except InterfaceError:
            return

    def close(self) -> None:
        # закрытие подключения к базе данных (сессии)
        self.__connection.close()

    def commit(self) -> None:
        # запись в базу данных
        if not self.autocommit:
            self.__connection.commit()

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
