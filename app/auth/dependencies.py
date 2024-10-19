from typing import Annotated
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Depends, Response, Cookie, Form, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.tokens import (
    JWTDecoder,
    AccessTokenEncoder,
    RefreshTokenEncoder,
    get_jwt_decoder
)
from auth.models import (
    UserModel,
    ExtendedUserModel,
    AccessTokenModel,
    PayloadTokenModel
)
from auth.redis_client import RedisClient, get_redis_client
from auth.exceptions import NonExistentUserError, NonExistentTokenError
from auth.hashing_psw import get_password_hash, verify_password
from core.database import UserDataAccessObject, get_user_dao
from core.settings import config
from utils import Converter


http_bearer = HTTPBearer()


class RegistrationService:
    def __init__(
            self,
            access_token_encoder: AccessTokenEncoder = AccessTokenEncoder(),
            refresh_token_encoder: RefreshTokenEncoder = RefreshTokenEncoder(),
            redis_client: RedisClient = get_redis_client(),
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.access_token_encoder = access_token_encoder
        self.refresh_token_encoder = refresh_token_encoder
        self.redis_client = redis_client
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            response: Response,
            username: Annotated[str, Form(min_length=6, max_length=16)],
            password: Annotated[str, Form(min_length=8, max_length=18)]
    ) -> ExtendedUserModel:
        if self.user_data_access_obj.get_user_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='username is alredy taken'
            )

        user = self.user_data_access_obj.create(
            username,
            get_password_hash(password)
        )
        user = self.converter(user)[0]

        access_token = self.access_token_encoder(user)
        refresh_token = self.refresh_token_encoder(user)
        set_refresh_cookie(response, refresh_token)
        self.redis_client.append_token(user.user_id, refresh_token)

        return ExtendedUserModel(
            user=user,
            token=AccessTokenModel(
                access_token=access_token
            )
        )


class LoginService:
    def __init__(
            self,
            access_token_encoder: AccessTokenEncoder = AccessTokenEncoder(),
            refresh_token_encoder: RefreshTokenEncoder = RefreshTokenEncoder(),
            redis_client: RedisClient = get_redis_client(),
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.access_token_encoder = access_token_encoder
        self.refresh_token_encoder = refresh_token_encoder
        self.redis_client = redis_client
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            response: Response,
            username: Annotated[str, Form(min_length=6, max_length=16)],
            password: Annotated[str, Form(min_length=8, max_length=18)]
    ) -> ExtendedUserModel:
        user = self.user_data_access_obj.get_user_by_username(username)

        if not user:
            raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail="incorrect username or password"
            )

        user[0] = list(user[0])
        hashed_password = user[0].pop(-1)

        if not verify_password(password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="incorrect username or password"
            )

        user = self.converter(user)[0]

        access_token = self.access_token_encoder(user)
        refresh_token = self.refresh_token_encoder(user)
        set_refresh_cookie(response, refresh_token)
        self.redis_client.append_token(user.user_id, refresh_token)

        return ExtendedUserModel(
            user=user,
            token=AccessTokenModel(
                access_token=access_token
            )
        )


class LogoutService:
    def __init__(
            self,
            jwt_decoder: JWTDecoder = get_jwt_decoder(),
            redis_client: RedisClient = get_redis_client()
    ):
        self.jwt_decoder = jwt_decoder
        self.redis_client = redis_client

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str | None, Cookie()] = None
    ) -> None:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='unauthorized'
            )

        try:
            response.delete_cookie(config.COOKIE_KEY)
            payload = self.jwt_decoder(refresh_token)
            self.redis_client.delete_token(payload['sub'], refresh_token)
        except NonExistentTokenError:
            # если refresh токена в redis нет - им кто-то уже воспользовался
            # для безопасности пользователя
            # следует удалить все его refresh токены

            self.redis_client.delete_user(payload['sub'])

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )
        except (InvalidTokenError, NonExistentUserError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class TokenRefreshService:
    def __init__(
            self,
            jwt_decoder: JWTDecoder = get_jwt_decoder(),
            access_token_encoder: AccessTokenEncoder = AccessTokenEncoder(),
            refresh_token_encoder: RefreshTokenEncoder = RefreshTokenEncoder(),
            redis_client: RedisClient = get_redis_client()
    ):
        self.jwt_decoder = jwt_decoder
        self.access_token_encoder = access_token_encoder
        self.refresh_token_encoder = refresh_token_encoder
        self.redis_client = redis_client

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str | None, Cookie()] = None
    ) -> AccessTokenModel:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='unauthorized'
            )

        try:
            response.delete_cookie(config.COOKIE_KEY)
            payload = PayloadTokenModel(**self.jwt_decoder(refresh_token))
            self.redis_client.delete_token(payload.sub, refresh_token)

            refresh_token = self.refresh_token_encoder(payload)
            access_token = self.access_token_encoder(payload)

            set_refresh_cookie(response, refresh_token)
            self.redis_client.append_token(payload.sub, refresh_token)

            return AccessTokenModel(
                access_token=access_token
            )
        except NonExistentTokenError:
            # если рефреш токена нет в redis - им кто-то
            # воспользовался вместо пользователя
            # (удалим все рефреш токены пользователя у себя,
            # тем самым удалив и токен злоумышленника)

            self.redis_client.delete_user(payload.sub)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )
        except (InvalidTokenError, NonExistentUserError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class AccessTokenValidationService:
    """Валидация access токена из заголовков"""

    def __init__(self, jwt_decoder: JWTDecoder = get_jwt_decoder()):
        self.jwt_decoder = jwt_decoder

    def __call__(
            self,
            token: Annotated[
                HTTPAuthorizationCredentials, Depends(http_bearer)
            ]
    ) -> PayloadTokenModel:
        try:
            return PayloadTokenModel(**self.jwt_decoder(token.credentials))
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


access_token_validation_service = AccessTokenValidationService()


class AuthorizationService:
    def __init__(
            self,
            min_role_id: int,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.__min_role_id = min_role_id
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[
                PayloadTokenModel, Depends(access_token_validation_service)
            ]
    ) -> PayloadTokenModel:
        if self.__min_role_id > 1:
            user = self.user_data_access_obj.read(payload.sub)
            user = self.converter(user)[0]

            if not self.__min_role_id <= user.role_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='you do not have such rights'
                )

        return payload


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    # устанавливаем refresh токен в cookie

    max_age = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=config.COOKIE_KEY,
        value=refresh_token,
        max_age=max_age,
        httponly=True
    )


# dependencies
registration_service = RegistrationService()
login_service = LoginService()
logout_service = LogoutService()
token_refresh_service = TokenRefreshService()
