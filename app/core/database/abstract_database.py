from abc import ABC, abstractmethod


class AbstractDataBase(ABC):
    """
    Абстрактный класс для работы с базой данных.
    От него наследовать отдельные классы, которые будут выполнять
    CRUD-операции с конкретным типом данных в бд: будь то комментарии, юзеры или товары.
    """

    def __init__(self, cursor):
        # если че, на данный момент развития курсоры берутся
        # из метода get_cursor класса BaseSession
        self.cursor = cursor

    def __del__(self):
        self.cursor.close()

    def close_cursor(self):
        self.cursor.close()

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
