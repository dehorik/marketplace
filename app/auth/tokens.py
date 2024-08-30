import jwt
from typing import Any
from pathlib import Path

from core.config_reader import config


class EncodeJWT:
    def __init__(
            self,
            private_key: str = Path(config.getenv('PRIVATE_KEY_PATH')).read_text(),
            algorithm: str = config.getenv('ALGORITHM')
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


class DecodeJWT:
    def __init__(
            self,
            public_key: str = Path(config.getenv('PUBLIC_KEY_PATH')).read_text(),
            algorithm: str = config.getenv('ALGORITHM')
    ):
        self.__public_key = public_key
        self.__algorithm = algorithm

    def __call__(self, token: str | bytes) -> Any:
        dt = jwt.decode(
            jwt=token,
            key=self.__public_key,
            algorithms=[self.__algorithm]
        )

        return dt


class CreateRefreshToken:
    def __init__(
            self,
            jwt_encoder: EncodeJWT = EncodeJWT(),
            exp_minutes: int = config.getenv('REFRESH_TOKEN_EXPIRE_MINUTES')
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_minutes

    def __call__(self, user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": self.__exp_minutes
        }

        return self.__jwt_encoder(payload)


class CreateAccessToken:
    def __init__(
            self,
            jwt_encoder: EncodeJWT = EncodeJWT(),
            exp_minutes: int = config.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
    ):
        self.__jwt_encoder = jwt_encoder
        self.__exp_minutes = exp_minutes

    def __call__(self, user_id: int, role_id: int, user_name: str) -> str:
        paylaod = {
            "user_id": user_id,
            "role_id": role_id,
            "user_name": user_name,
            "exp": self.__exp_minutes
        }

        return self.__jwt_encoder(paylaod)


class CreateTokensModel:
    def __init__(self, tokens_model):
        self.__tokens_model = tokens_model

    def __call__(self, user_id: int, role_id: int, user_name: str):
        refresh_token_creator = CreateRefreshToken()
        access_token_creator = CreateAccessToken()

        tokens = {
            "refresh_token": refresh_token_creator(user_id),
            "access_token": access_token_creator(user_id, role_id, user_name)
        }

        return self.__tokens_model(**tokens)
