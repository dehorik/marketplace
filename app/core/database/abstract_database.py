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
        # Этот метод не рекомендую использовать, так как можно словить исключение
        # из-за попытки закрыть курсор, который уже закрыт.
        # Курсор сам закроется, когда все ссылки с объекта съест сборщик мусора

        self.cursor.close()

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def read(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass
