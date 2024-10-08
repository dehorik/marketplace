class RedisError(Exception):
    """Базовый класс для всех исключений RedisClient"""
    pass

class NonExistentUserError(RedisError):
    """Бросать, если user_id не найден"""
    pass

class NonExistentTokenError(RedisError):
    """Бросать, если refresh токен не найден"""
    pass
