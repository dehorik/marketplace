from uuid import uuid4


class IDGenerator:
    """Генератор уникальных идентификаторов"""

    def __init__(self, func=uuid4):
        self.__func_generator = func

    def __call__(self):
        return str(self.__func_generator())

