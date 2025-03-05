from typing import Annotated
from datetime import datetime, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Depends, Response, Cookie, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg2.errors import RaiseException

from auth.tokens import (
    JWTDecoder,
    AccessTokenEncoder,
    RefreshTokenEncoder,
    get_jwt_decoder
)
from auth.models import (
    CredentialsModel,
    UserModel,
    ExtendedUserModel,
    AccessTokenModel,
    TokenPayloadModel
)
from auth.redis_client import RedisClient, get_redis_client
from auth.hashing_psw import get_password_hash, verify_password
from auth.exceptions import NonExistentUserError
from core.database import UserDataAccessObject, get_user_dao
from core.settings import config
from utils import Converter


http_bearer = HTTPBearer()


class RegistrationService:
    """Регистрация"""

    def __init__(
            self,
            access_token_encoder: AccessTokenEncoder,
            refresh_token_encoder: RefreshTokenEncoder,
            redis_client: RedisClient,
            user_dao: UserDataAccessObject,
            converter: Converter
    ):
        self.access_token_encoder = access_token_encoder
        self.refresh_token_encoder = refresh_token_encoder
        self.redis_client = redis_client
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            response: Response,
            credentilas: CredentialsModel
    ) -> ExtendedUserModel:
        try:
            user = self.user_data_access_obj.create(
                credentilas.username,
                get_password_hash(credentilas.password),
                datetime.now(timezone.utc).date()
            )
            user = self.converter.fetchone(user)

            access_token = self.access_token_encoder(user)
            refresh_token = self.refresh_token_encoder(user)
            set_refresh_cookie(response, refresh_token)
            set_user_id_cookie(response, str(user.user_id))
            self.redis_client.append_token(user.user_id, refresh_token)

            return ExtendedUserModel(
                user=user,
                token=AccessTokenModel(access_token=access_token)
            )
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='username is alredy taken'
            )


class LoginService:
    """Вход в аккаунт"""

    def __init__(
            self,
            access_token_encoder: AccessTokenEncoder,
            refresh_token_encoder: RefreshTokenEncoder,
            redis_client: RedisClient,
            user_dao: UserDataAccessObject,
            converter: Converter
    ):
        self.access_token_encoder = access_token_encoder
        self.refresh_token_encoder = refresh_token_encoder
        self.redis_client = redis_client
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            response: Response,
            credentilas: CredentialsModel
    ) -> ExtendedUserModel:
        try:
            user = self.user_data_access_obj.get_user_by_username(credentilas.username)
            hashed_password = user[-1]
            user = self.converter.fetchone(user[:-1])

            if not verify_password(credentilas.password, hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="incorrect username or password"
                )

            access_token = self.access_token_encoder(user)
            refresh_token = self.refresh_token_encoder(user)
            set_refresh_cookie(response, refresh_token)
            set_user_id_cookie(response, str(user.user_id))
            self.redis_client.append_token(user.user_id, refresh_token)

            return ExtendedUserModel(
                user=user,
                token=AccessTokenModel(access_token=access_token)
            )
        except (ValueError, IndexError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="incorrect username or password"
            )


class RefreshTokenValidationService:
    """Валидация refresh токена из cookie"""

    def __init__(
            self,
            jwt_decoder: JWTDecoder,
            redis_client: RedisClient
    ):
        self.jwt_decoder = jwt_decoder
        self.redis_client = redis_client

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str | None, Cookie()] = None
    ) -> str:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='not authenticated'
            )

        try:
            payload = self.jwt_decoder(refresh_token)
            payload = TokenPayloadModel(**payload)

            if refresh_token not in self.redis_client.get_tokens(payload.sub):
                # если refresh токена в redis нет - им кто-то уже воспользовался;
                # для безопасности пользователя следует удалить все его refresh токены

                response.delete_cookie(config.REFRESH_COOKIE_KEY)
                response.delete_cookie(config.USER_ID_COOKIE_KEY)
                self.redis_client.delete_user(payload.sub)

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='not authenticated'
                )

            return refresh_token
        except (InvalidTokenError, NonExistentUserError):
            response.delete_cookie(config.REFRESH_COOKIE_KEY)
            response.delete_cookie(config.USER_ID_COOKIE_KEY)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='not authenticated'
            )


refresh_token_validation_service = RefreshTokenValidationService(
    jwt_decoder=get_jwt_decoder(),
    redis_client=get_redis_client()
)


class LogoutService:
    """Выход из аккаунта"""

    def __init__(
            self,
            jwt_decoder: JWTDecoder,
            redis_client: RedisClient
    ):
        self.jwt_decoder = jwt_decoder
        self.redis_client = redis_client

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str, Depends(refresh_token_validation_service)]
    ) -> dict:
        payload = self.jwt_decoder(refresh_token)
        payload = TokenPayloadModel(**payload)
        response.delete_cookie(config.REFRESH_COOKIE_KEY)
        response.delete_cookie(config.USER_ID_COOKIE_KEY)
        self.redis_client.delete_token(payload.sub, refresh_token)

        return {
            "message": "successful logout"
        }


class TokenRefreshService:
    """Выпуск новой пары токенов с помощью refresh токена"""

    def __init__(
            self,
            jwt_decoder: JWTDecoder,
            access_token_encoder: AccessTokenEncoder,
            refresh_token_encoder: RefreshTokenEncoder,
            redis_client: RedisClient
    ):
        self.jwt_decoder = jwt_decoder
        self.access_token_encoder = access_token_encoder
        self.refresh_token_encoder = refresh_token_encoder
        self.redis_client = redis_client

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str, Depends(refresh_token_validation_service)]
    ) -> AccessTokenModel:
        payload = self.jwt_decoder(refresh_token)
        payload = TokenPayloadModel(**payload)
        response.delete_cookie(config.REFRESH_COOKIE_KEY)
        response.delete_cookie(config.USER_ID_COOKIE_KEY)
        self.redis_client.delete_token(payload.sub, refresh_token)

        refresh_token = self.refresh_token_encoder(payload)
        access_token = self.access_token_encoder(payload)
        set_refresh_cookie(response, refresh_token)
        set_user_id_cookie(response, str(payload.sub))
        self.redis_client.append_token(payload.sub, refresh_token)

        return AccessTokenModel(access_token=access_token)


class AccessTokenValidationService:
    """Валидация access токена из заголовков"""

    def __init__(self, jwt_decoder: JWTDecoder):
        self.jwt_decoder = jwt_decoder

    def __call__(
            self,
            token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
    ) -> TokenPayloadModel:
        try:
            payload = self.jwt_decoder(token.credentials)
            payload = TokenPayloadModel(**payload)

            return payload
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='not authenticated'
            )


access_token_validation_service = AccessTokenValidationService(
    jwt_decoder=get_jwt_decoder()
)


class AuthorizationService:
    """Авторизация"""

    def __init__(
            self,
            min_role_id: int,
            user_dao: UserDataAccessObject,
            converter: Converter
    ):
        # min_role_id - id минимальной роли, необходимой для доступа к эндпоинту

        self.__min_role_id = min_role_id
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(access_token_validation_service)]
    ) -> TokenPayloadModel:
        try:
            if self.__min_role_id > 1:
                user = self.user_data_access_obj.read(payload.sub)
                user = self.converter.fetchone(user)

                if not self.__min_role_id <= user.role_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail='forbidden'
                    )

            return payload
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="not authenticated"
            )


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """устанавливает refresh токен в cookie"""

    max_age = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=config.REFRESH_COOKIE_KEY,
        value=refresh_token,
        max_age=max_age,
        httponly=True
    )

def set_user_id_cookie(response: Response, user_id: str) -> None:
    """устанавливает user_id в cookie"""

    max_age = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=config.USER_ID_COOKIE_KEY,
        value=user_id,
        max_age=max_age,
        httponly=True
    )


registration_service = RegistrationService(
    access_token_encoder=AccessTokenEncoder(),
    refresh_token_encoder=RefreshTokenEncoder(),
    redis_client=get_redis_client(),
    user_dao=get_user_dao(),
    converter=Converter(UserModel)
)

login_service = LoginService(
    access_token_encoder=AccessTokenEncoder(),
    refresh_token_encoder=RefreshTokenEncoder(),
    redis_client=get_redis_client(),
    user_dao=get_user_dao(),
    converter=Converter(UserModel)
)

logout_service = LogoutService(
    jwt_decoder=get_jwt_decoder(),
    redis_client=get_redis_client()
)

token_refresh_service = TokenRefreshService(
    jwt_decoder=get_jwt_decoder(),
    access_token_encoder=AccessTokenEncoder(),
    refresh_token_encoder=RefreshTokenEncoder(),
    redis_client=get_redis_client()
)

user_dependency = AuthorizationService(
    min_role_id=1,
    user_dao=get_user_dao(),
    converter=Converter(UserModel)
)

admin_dependency = AuthorizationService(
    min_role_id=2,
    user_dao=get_user_dao(),
    converter=Converter(UserModel)
)

superuser_dependency = AuthorizationService(
    min_role_id=3,
    user_dao=get_user_dao(),
    converter=Converter(UserModel)
)
