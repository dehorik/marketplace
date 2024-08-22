from core.database import Session
from core.database.interface_database import InterfaceDataBase

class UserDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD-операций с пользователями"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self):
        self.__session.commit()
        self.__cursor.close()

    def commit(self):
        self.__session.commit()

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
