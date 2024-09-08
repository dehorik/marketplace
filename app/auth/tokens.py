import jwt
import datetime
from pathlib import Path

from auth.models import PayloadTokenModel
from auth.exceptions import InvalidPayloadObjectException
from entities.users.models import UserModel
from core.settings import config


class JWTEncoder:
    """Универсальный класс для выпуска токенов"""

    def __init__(
            self,
            private_key: str = Path(f"../{config.PRIVATE_KEY_PATH}").read_text(),
            algorithm: str = config.ALGORITHM
    ):
        self.__private_key = private_key
        self.__algorithm = algorithm

    def __call__(self, payload: dict) -> str:
        token = jwt.encode(
            payload=payload,
            key=self.__private_key,
            algorithm=self.__algorithm
        )

        return token


class JWTDecoder:
    """Универсальный класс для декодирования токенов"""

    def __init__(
            self,
            public_key: str = Path(f'../{config.PUBLIC_KEY_PATH}').read_text(),
            algorithm: str = config.ALGORITHM
    ):
        self.__public_key = public_key
        self.__algorithm = algorithm

    def __call__(self, token: str | bytes) -> dict:
        dt = jwt.decode(
            jwt=token,
            key=self.__public_key,
            algorithms=[self.__algorithm]
        )

        return dt


class AccessTokenCreator:
    """Для выпуска access токенов"""

    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            exp_minutes: int = config.ACCESS_TOKEN_EXPIRE_MINUTES
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_minutes

    def __call__(self, data: UserModel | PayloadTokenModel) -> str:
        if type(data) is not UserModel and type(data) is not PayloadTokenModel:
            raise InvalidPayloadObjectException('invalid payload object')

        sub = data.user_id if type(data) is UserModel else data.sub
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "token_type": "access",
            "sub": sub,
            "role_id": data.role_id,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=self.__exp_minutes)
        }

        return self.__jwt_encoder(payload)


class RefreshTokenCreator:
    """Для выпуска refresh токенов"""

    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            exp_days: int = config.REFRESH_TOKEN_EXPIRE_DAYS
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_days * 24 * 60

    def __call__(self, data: UserModel | PayloadTokenModel) -> str:
        if type(data) is not UserModel and type(data) is not PayloadTokenModel:
            raise InvalidPayloadObjectException('invalid payload object')

        sub = data.user_id if type(data) is UserModel else data.sub
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "token_type": "refresh",
            "sub": sub,
            "role_id": data.role_id,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=self.__exp_minutes)
        }

        return self.__jwt_encoder(payload)
