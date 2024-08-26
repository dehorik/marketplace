from uuid import uuid4, UUID


class IDGenerator:
    """Генератор уникальных идентификаторов"""

    def __init__(self, func=uuid4):
        self.__func_generator = func

    def __call__(self) -> UUID:
        return self.__func_generator()
