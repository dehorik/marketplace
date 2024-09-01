from typing import Annotated, Tuple
from fastapi import HTTPException, Depends, Response, status
from fastapi.security import HTTPBearer

from auth.tokens import (
    JWTEncoder,
    JWTDecoder,
    AccessTokenCreator,
    RefreshTokenCreator
)
from auth.models import (
    UserCredentialsModel,
    AuthorizationModel,
    AccessTokenModel,
    UserModel
)
from auth.redis_client import RedisClient
from auth.hashing_psw import get_password_hash
from core.settings import config
from core.database import UserDataBase
from utils import Converter


http_bearer = HTTPBearer()


class BaseDependency:
    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            jwt_decoder: JWTDecoder = JWTDecoder(),
            access_token_creator: AccessTokenCreator = AccessTokenCreator(),
            refresh_token_creator: RefreshTokenCreator = RefreshTokenCreator(),
            redis_client: RedisClient = RedisClient(),
            user_database: Annotated[type, UserDataBase] = UserDataBase
    ):
        self.jwt_encoder = jwt_encoder
        self.jwt_decoder = jwt_decoder
        self.access_token_creator = access_token_creator
        self.refresh_token_creator = refresh_token_creator
        self.redis_client = redis_client
        self.user_database = user_database


class VerifyUser(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            credentilas: UserCredentialsModel
    ) -> UserModel:
        with self.user_database() as user_db:
            user = user_db.get_user_by_credentials(
                credentilas.user_name,
                get_password_hash(credentilas.user_password)
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="incorrect username or password"
                )

            return self.converter.serialization(user)[0]


class GenerateTokens(BaseDependency):
    def __call__(
            self,
            response: Response,
            user: Annotated[UserModel, Depends(VerifyUser())]
    ) -> Tuple[UserModel, str]:
        access_token = self.access_token_creator(user)
        refresh_token = self.refresh_token_creator(user)

        cookie_max_age = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=cookie_max_age,
            httponly=True
        )

        self.redis_client.push_token(user.user_id, refresh_token)

        return user, access_token


class Login(BaseDependency):
    def __call__(
            self,
            tp: Annotated[tuple, Depends(GenerateTokens())]
    ) -> AuthorizationModel:
        user, access_token = tp
        access_token = AccessTokenModel(access_token=access_token)
        auth_model = AuthorizationModel(user=user, access_token=access_token)

        return auth_model

