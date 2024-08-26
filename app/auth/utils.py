from passlib.context import CryptContext
from uuid import uuid4


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPassword:
    """Хеширование паролей"""

    def __init__(self, user_password: str):
        self.__hashed_password = pwd_context.hash(user_password)

    def __str__(self) -> str:
        return self.__hashed_password

    @property
    def hashed_password(self) -> str:
        return self.__hashed_password


class SessionIdGenerator:
    """Генерация id сессий"""

    def __init__(self):
        self.__session_id = uuid4().hex

    def __str__(self) -> str:
        return self.__session_id

    @property
    def session_id(self) -> str:
        return self.__session_id
