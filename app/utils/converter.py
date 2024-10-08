class Converter:
    """Конвертер данных из строк базы данных в Pydantic модель"""

    def __init__(self, model):
        self.__model = model

    def __call__(self, rows: list) -> list:
        # из вида [(), ()...] в Pydantic модель

        lst = []

        for row in rows:
            keys = self.__model.__dict__['__annotations__'].keys()
            dt = {}

            for indx, key in enumerate(keys):
                dt[key] = row[indx]

            obj = self.__model(**dt)
            lst.append(obj)

        return lst
