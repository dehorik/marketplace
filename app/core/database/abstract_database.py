from abc import ABC, abstractmethod
from . import session_factory


class AbstractDataBase(ABC):
    def __init__(self, session: session_factory.BaseSession):
        self._cursor = session.get_cursor()

    def __del__(self):
        self._cursor.close()

    def close_cursor(self):
        self._cursor.close()

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
