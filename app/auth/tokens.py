import jwt
import datetime
from pathlib import Path

from core.settings import config
from entities.users.models import UserModel


class JWTEncoder:
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
    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            exp_minutes: float = config.ACCESS_TOKEN_EXPIRE_MINUTES
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_minutes

    def __call__(self, user: UserModel) -> str:
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "type": "access",
            "sub": user.user_id,
            "role_id": user.role_id,
            "user_name": user.user_name,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=self.__exp_minutes)
        }

        return self.__jwt_encoder(payload)


class RefreshTokenCreator:
    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            exp_days: float = config.REFRESH_TOKEN_EXPIRE_DAYS
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_days * 24 * 60

    def __call__(self, user: UserModel) -> str:
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "type": "refresh",
            "sub": user.user_id,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=self.__exp_minutes)
        }

        return self.__jwt_encoder(payload)
