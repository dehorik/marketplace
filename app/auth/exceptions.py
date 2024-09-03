class RedisException(Exception):
    pass


class InvalidUserException(RedisException):
    pass


class InvalidTokenException(RedisException):
    pass
