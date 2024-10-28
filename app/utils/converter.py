from typing import Any, List, Union


class Converter:
    """Конвертер данных из строк базы данных в pydantic модель"""

    def __init__(self, model):
        self.__class__.fetchone.__annotations__["return"] = model
        self.__class__.fetchmany.__annotations__["return"] = List[model]

        self.__model = model

    @staticmethod
    def __check_lst(lst: list | tuple) -> None:
        if lst is None:
            raise ValueError("expected list or tuple; got None instead")

    def fetchone(self, row: list | tuple) -> Any:
        self.__check_lst(row)

        keys = self.__model.__dict__['__annotations__'].keys()
        dt = {}

        for indx, key in enumerate(keys):
            dt[key] = row[indx]

        return self.__model(**dt)

    def fetchmany(self, rows: List[Union[list, tuple]]) -> Any:
        self.__check_lst(rows)

        lst = []

        for row in rows:
            keys = self.__model.__dict__['__annotations__'].keys()
            dt = {}

            for indx, key in enumerate(keys):
                dt[key] = row[indx]

            obj = self.__model(**dt)
            lst.append(obj)

        return lst
