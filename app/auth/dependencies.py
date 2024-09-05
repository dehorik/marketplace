import datetime
from typing import Annotated
from fastapi import HTTPException, Depends, Response, Cookie, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from auth.tokens import (
    JWTEncoder,
    JWTDecoder,
    AccessTokenCreator,
    RefreshTokenCreator
)
from auth.models import (
    FullPayloadTokenModel,
    UserCredentialsModel,
    AuthorizationModel,
    AccessTokenModel,
    PayloadTokenModel,
    UserModel, LogoutModel
)
from auth.redis_client import RedisClient
from auth.exceptions import InvalidUserException, InvalidTokenException
from auth.hashing_psw import get_password_hash, verify_password
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


class AccessTokenValidator(BaseDependency):
    def __call__(
            self,
            token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
    ) -> FullPayloadTokenModel:
        try:
            payload = self.jwt_decoder(token.credentials)
            return FullPayloadTokenModel(**payload)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class CreateUser(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            credentials: UserCredentialsModel
    ) -> UserModel:
        with self.user_database() as user_db:
            user = user_db.get_user_by_user_name(credentials.user_name)
            if user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='username is alredy taken'
                )

            user = user_db.create(
                credentials.user_name,
                get_password_hash(credentials.user_password)
            )

            return self.converter.serialization(user)[0]


class Register(BaseDependency):
    def __call__(
            self,
            response: Response,
            user: Annotated[UserModel, Depends(CreateUser())]
    ) -> AuthorizationModel:
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

        access_token = AccessTokenModel(access_token=access_token)
        auth_model = AuthorizationModel(user=user, access_token=access_token)

        return auth_model


class VerifyUser(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            credentilas: UserCredentialsModel
    ) -> UserModel:
        with self.user_database() as user_db:
            user = user_db.get_user_by_user_name(credentilas.user_name)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="incorrect username or password"
                )

            user = [list(user) for user in user]
            user_hashed_password = user[0].pop(3)

            if not verify_password(credentilas.user_password, user_hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="incorrect username or password"
                )

            return self.converter.serialization(user)[0]


class Login(BaseDependency):
    def __call__(
            self,
            response: Response,
            user: Annotated[UserModel, Depends(VerifyUser())]
    ) -> AuthorizationModel:
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

        access_token = AccessTokenModel(access_token=access_token)
        auth_model = AuthorizationModel(user=user, access_token=access_token)

        return auth_model


class Logout(BaseDependency):
    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str | None, Cookie()] = None
    ) -> LogoutModel:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='unauthorized'
            )

        try:
            payload = self.jwt_decoder(refresh_token)

            self.redis_client.delete_token(payload['user_id'], refresh_token)
            response.delete_cookie('refresh_token')

            return LogoutModel()

        except InvalidTokenException:
            # noinspection PyUnboundLocalVariable
            self.redis_client.delete_user(payload['user_id'])

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )
        except (InvalidTokenError, InvalidUserException):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class ValidateTokens(BaseDependency):
    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str | None, Cookie()] = None
    ) -> dict:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='unauthorized'
            )

        try:
            payload = self.jwt_decoder(refresh_token)
            self.redis_client.delete_token(payload['user_id'], refresh_token)
            response.delete_cookie('refresh_token')

            return payload
        except InvalidTokenException:
            # noinspection PyUnboundLocalVariable
            self.redis_client.delete_user(payload['user_id'])

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )
        except (InvalidTokenError, InvalidUserException):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class Refresh(BaseDependency):
    def __call__(
            self,
            response: Response,
            payload: Annotated[dict, Depends(ValidateTokens())]
    ) -> AccessTokenModel:
        payload_token = PayloadTokenModel(
            token_type=payload['token_type'],
            user_id=payload['user_id'],
            role_id=payload['role_id'],
            user_name=payload['user_name']
        )

        refresh_token = self.refresh_token_creator(payload_token)
        self.redis_client.push_token(payload['sub'], refresh_token)

        #
        # настроить автоматическое удаление рефреш кук везде!!!!
        #

        now = datetime.datetime.now(datetime.UTC)
        exp_minutes = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        expires = now + datetime.timedelta(minutes=exp_minutes)
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            expires=expires,
            httponly=True
        )

        payload_token.token_type = 'access'
        access_token = self.access_token_creator(payload_token)

        return AccessTokenModel(access_token=access_token)


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    now = datetime.datetime.now(datetime.UTC)
    exp_minutes = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    expires = now + datetime.timedelta(minutes=exp_minutes)

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        expires=expires,
        httponly=True
    )
