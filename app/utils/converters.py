from abc import ABC, abstractmethod


class InterfaceConverter(ABC):
    """
    Интерфейс для классов-конвертеров данных
    из строк БД в pydantic-модели и наоборот
    """

    @abstractmethod
    def serialization(self, *args, **kwargs):
        # из вида [(), ()...] в Pydantic модель
        pass

    @abstractmethod
    def deserialization(self, *args, **kwargs):
        # из Pydantic модели в вид [(), ()...]
        pass


class ProductConverter(InterfaceConverter):
    def __init__(self, model):
        self.__model = model

    def serialization(self, rows: list) -> list:
        lst = []

        for row in rows:
            keys = self.__model.__dict__['__annotations__'].keys()
            dt = {}

            for indx, key in enumerate(keys):
                dt[key] = row[indx]

            obj = self.__model(**dt)
            lst.append(obj)

        return lst

    def deserialization(self, lst_obj: list) -> list:
        lst_rows = []

        for obj in lst_obj:
            dt = obj.dump()
            row = tuple(dt.values())
            lst_rows.append(row)

        return lst_rows
