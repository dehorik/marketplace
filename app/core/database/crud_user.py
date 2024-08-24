from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase

class UserDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с пользователями"""

    def __init__(self, session: Session):
        self.__session = session
        self._cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__session.commit()
        self._cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
