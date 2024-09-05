class RedisException(Exception):
    """Базовый класс для всех исключений RedisClient"""
    pass


class InvalidDataObject(RedisException):
    """
    Бросать, если для создания подключения
    передан невалидный объект
    """
    pass

class InvalidUserException(RedisException):
    """Бросать, если user_id не найден"""
    pass


class InvalidTokenException(RedisException):
    """Бросать, если refresh токен не найден"""
    pass


class TokenException(Exception):
    """Базовый класс для пользовательских исключений при работе с jwt"""
    pass


class InvalidPayloadObjectException(TokenException):
    """Бросать при попытке выпустить jwt с невалидным payload"""
    pass
