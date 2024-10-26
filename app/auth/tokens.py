from pathlib import Path
from datetime import UTC, datetime, timedelta
import jwt

from auth.models import PayloadTokenModel, UserModel
from core.settings import config


class JWTEncoder:
    """Универсальный класс для выпуска токенов"""

    def __init__(self, private_key: str, algorithm: str):
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

    def __init__(self, public_key: str, algorithm: str):
        self.__public_key = public_key
        self.__algorithm = algorithm

    def __call__(self, token: str | bytes) -> dict:
        payload = jwt.decode(
            jwt=token,
            key=self.__public_key,
            algorithms=[self.__algorithm]
        )

        return payload


def get_jwt_encoder() -> JWTEncoder:
    return JWTEncoder(
        Path(config.PRIVATE_KEY_PATH).read_text(),
        config.ALGORITHM
    )

def get_jwt_decoder() -> JWTDecoder:
    return JWTDecoder(
        Path(config.PUBLIC_KEY_PATH).read_text(),
        config.ALGORITHM
    )


class AccessTokenEncoder:
    """Для выпуска access токенов"""

    def __init__(
            self,
            jwt_encoder: JWTEncoder = get_jwt_encoder(),
            exp_minutes: int = config.ACCESS_TOKEN_EXPIRE_MINUTES
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_minutes

    def __call__(self, data: UserModel | PayloadTokenModel) -> str:
        if type(data) is not UserModel and type(data) is not PayloadTokenModel:
            raise TypeError('invalid payload object')

        sub = data.user_id if type(data) is UserModel else data.sub
        now = datetime.now(UTC)
        payload = {
            "token_type": "access",
            "sub": sub,
            "iat": now,
            "exp": now + timedelta(minutes=self.__exp_minutes)
        }

        return self.__jwt_encoder(payload)


class RefreshTokenEncoder:
    """Для выпуска refresh токенов"""

    def __init__(
            self,
            jwt_encoder: JWTEncoder = get_jwt_encoder(),
            exp_days: int = config.REFRESH_TOKEN_EXPIRE_DAYS
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_days * 24 * 60

    def __call__(self, data: UserModel | PayloadTokenModel) -> str:
        if type(data) is not UserModel and type(data) is not PayloadTokenModel:
            raise TypeError('invalid payload object')

        sub = data.user_id if type(data) is UserModel else data.sub
        now = datetime.now(UTC)
        payload = {
            "token_type": "refresh",
            "sub": sub,
            "iat": now,
            "exp": now + timedelta(minutes=self.__exp_minutes)
        }

        return self.__jwt_encoder(payload)
