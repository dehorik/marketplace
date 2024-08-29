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
