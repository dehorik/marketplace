from abc import ABC, abstractmethod


class InterfaceDataAccessObject(ABC):
    """
    Интерфейс для классов, создающих объекты доступа к данным из БД.
    От него наследовать классы, которые будут выполнять
    crud операции с конкретным ресурсом.
    """

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
