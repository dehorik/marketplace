import psycopg2

from . import singleton
from ..config_reader import config


class BaseSession(singleton.Singleton):
    def __init__(self):
        self.__connection = psycopg2.connect(
            dbname=config.getenv("DATABASE"),
            user=config.getenv("DATABASE_USER"),
            password=config.getenv("DATABASE_USER_PASSWORD"),
            host=config.getenv("DATABASE_HOST"),
            port=config.getenv("DATABASE_PORT")
        )

    def __del__(self):
        self.__connection.commit()
        self.__connection.close()

    def close_connection(self) -> None:
        self.__connection.commit()
        self.__connection.close()

    def get_cursor(self):
        return self.__connection.cursor()

