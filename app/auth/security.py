from passlib.context import CryptContext

from utils import IDGenerator


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashPassword:
    def __call__(self, user_password: str) -> str:
        return pwd_context.hash(user_password)


class SessionIdGenerator:
    def __call__(self) -> str:
        uuid_generator = IDGenerator()
        return uuid_generator().hex
