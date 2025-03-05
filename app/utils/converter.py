from typing import Any, List


class Converter:
    """Конвертер данных из строк, возвращаемых psycopg2, в pydantic модель"""

    def __init__(self, model):
        self.__model = model

    def fetchone(self, row: tuple) -> Any:
        """Использовать, когда sql запрос возвращает одну строку"""

        if row is None:
            raise ValueError("expected list or tuple; got None instead")

        keys = self.__model.__dict__['__annotations__'].keys()
        dt = {}

        for indx, key in enumerate(keys):
            dt[key] = row[indx]

        return self.__model(**dt)

    def fetchmany(self, rows: List[tuple]) -> Any:
        """Использовать, когда sql запрос возвращает несколько строк"""

        lst = []

        for row in rows:
            keys = self.__model.__dict__['__annotations__'].keys()
            dt = {}

            for indx, key in enumerate(keys):
                dt[key] = row[indx]

            obj = self.__model(**dt)
            lst.append(obj)

        return lst
