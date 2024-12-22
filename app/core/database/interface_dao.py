from abc import ABC, abstractmethod


class InterfaceDataAccessObject(ABC):
    """
    Интерфейс для классов, создающих объекты для доступа к данным из БД.
    От него наследовать отдельные классы, которые будут выполнять
    crud операции с конкретным типом данных.
    """

    @abstractmethod
    def __del__(self):
        pass

    @abstractmethod
    def close(self):
        # вызывать этот метод по завершении работы с объектом
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
