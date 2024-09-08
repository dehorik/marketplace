from abc import ABC, abstractmethod


class InterfaceDataBase(ABC):
    """
    Интерфейс для классов работы с БД.
    От него наследовать отдельные классы, которые будут выполнять
    CRUD операции с конкретным типом данных в бд.
    """

    @abstractmethod
    def __enter__(self):
        # отдавать созданный объект
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        # вызывать у объекта метод close()
        pass

    @abstractmethod
    def close(self):
        # вызывать этот метод при завершении работы с объектом
        pass

    @abstractmethod
    def commit(self):
        # вызывать этот метод для внесения изменений в БД
        pass

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
