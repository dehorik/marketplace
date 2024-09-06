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
    UserModel,
    UserCredentialsModel,
    AuthenticationModel,
    AccessTokenModel,
    PayloadTokenModel
)
from auth.redis_client import RedisClient
from auth.exceptions import InvalidUserException, InvalidTokenException
from auth.hashing_psw import get_password_hash, verify_password
from core.settings import config
from core.database import UserDataBase
from utils import Converter


http_bearer = HTTPBearer()


class BaseDependency:
    """
    Базовый класс, предоставляющий зависимостям
    ссылки на необходимые объекты
    """

    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            jwt_decoder: JWTDecoder = JWTDecoder(),
            access_token_creator: AccessTokenCreator = AccessTokenCreator(),
            refresh_token_creator: RefreshTokenCreator = RefreshTokenCreator(),
            redis_client: RedisClient = RedisClient(),
            user_database: Annotated[type, UserDataBase] = UserDataBase
    ):
        """
        :param jwt_encoder: объект для выпуска jwt
        :param jwt_decoder: объект для декодирования jwt
        :param access_token_creator: объект для выпуска access jwt
        :param refresh_token_creator: объект для выпуска refresh jwt
        :param redis_client: объект для работы с Redis
        :param user_database: ссылка на класс для работы с БД
        """

        self.jwt_encoder = jwt_encoder
        self.jwt_decoder = jwt_decoder
        self.access_token_creator = access_token_creator
        self.refresh_token_creator = refresh_token_creator
        self.redis_client = redis_client
        self.user_database = user_database


class UserCreator(BaseDependency):
    """Создание пользователя при регистрации"""

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


class Registration(BaseDependency):
    """Выпуск токенов для только что зарегистрировавшегося пользователя"""

    def __call__(
            self,
            response: Response,
            user: Annotated[UserModel, Depends(UserCreator())]
    ) -> AuthenticationModel:
        access_token = self.access_token_creator(user)
        refresh_token = self.refresh_token_creator(user)

        self.redis_client.append_token(user.user_id, refresh_token)
        set_refresh_cookie(response, refresh_token)

        auth_model = AuthenticationModel(
            user=user,
            access_token=AccessTokenModel(access_token=access_token)
        )

        return auth_model


class CredentialsVerifier(BaseDependency):
    """Проверка данных для входа"""

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

            user = list(user[0])
            user_hashed_password = user.pop(3)

            if not verify_password(credentilas.user_password, user_hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="incorrect username or password"
                )

            return self.converter.serialization([user])[0]


class Login(BaseDependency):
    """Выпуск токенов для только что вошедшего пользователя"""

    def __call__(
            self,
            response: Response,
            user: Annotated[UserModel, Depends(CredentialsVerifier())]
    ) -> AuthenticationModel:
        access_token = self.access_token_creator(user)
        refresh_token = self.refresh_token_creator(user)

        self.redis_client.append_token(user.user_id, refresh_token)
        set_refresh_cookie(response, refresh_token)

        auth_model = AuthenticationModel(
            user=user,
            access_token=AccessTokenModel(access_token=access_token)
        )

        return auth_model


class Logout(BaseDependency):
    """Выход из аккаунта"""

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str | None, Cookie()] = None
    ) -> str:
        if refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='unauthorized'
            )

        try:
            payload = self.jwt_decoder(refresh_token)
            self.redis_client.delete_token(payload['sub'], refresh_token)
            response.delete_cookie('refresh_token')

            return 'successful logout'

        except InvalidTokenException:
            # если refresh токена в redis нет - им кто-то уже воспользовался
            # noinspection PyUnboundLocalVariable
            self.redis_client.delete_user(payload['sub'])

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='invalid token'
            )
        except (InvalidTokenError, InvalidUserException):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class RefreshTokenValidator(BaseDependency):
    """Валидация refresh токена"""

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
            self.redis_client.delete_token(payload['sub'], refresh_token)
            response.delete_cookie('refresh_token')

            return payload
        except InvalidTokenException:
            # если рефреш токена нет в redis - им кто-то
            # воспользовался вместо пользователя
            # (удалим все рефреш токены пользователя у себя,
            # тем самым удалив и токен злоумышленника)

            # noinspection PyUnboundLocalVariable
            self.redis_client.delete_user(payload['sub'])

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='invalid token'
            )
        except (InvalidTokenError, InvalidUserException):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class Refresher(BaseDependency):
    """Выпуск пары токенов refresh/access на основе refresh токена"""

    def __call__(
            self,
            response: Response,
            payload: Annotated[dict, Depends(RefreshTokenValidator())]
    ) -> AccessTokenModel:
        payload_token = PayloadTokenModel(
            token_type=payload['token_type'],
            sub=payload['sub'],
            role_id=payload['role_id'],
            user_name=payload['user_name']
        )
        refresh_token = self.refresh_token_creator(payload_token)
        access_token = self.access_token_creator(payload_token)

        self.redis_client.append_token(payload['sub'], refresh_token)
        set_refresh_cookie(response, refresh_token)

        return AccessTokenModel(access_token=access_token)


class AccessTokenValidator(BaseDependency):
    """Для декодирования access токена из заголовков"""

    def __call__(
            self,
            token: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
    ) -> PayloadTokenModel:
        try:
            payload = self.jwt_decoder(token.credentials)
            return PayloadTokenModel(**payload)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid token'
            )


class Authorization(BaseDependency):
    """
    Авторизация пользователя
    (проверяем наличие прав на совершение каких-либо действий)
    """

    def __init__(self, min_role_id: int = 2):
        super().__init__()
        self.__min_role_id = min_role_id

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(AccessTokenValidator())]
    ) -> PayloadTokenModel:
        if not self.__min_role_id <= payload.role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='you have no such rights'
            )

        return payload


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    # устанавливаем refresh токен в cookie

    max_age = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        max_age=max_age,
        httponly=True
    )


# создание объектов-зависимостей для конечных точек;
# для корректной работы требуется прокинуть переменную
# аргументом в Depends() (не вызывать внутри);
# каждая зависимость использует метод __call__ для исполнения,
# а __init__ для внедрения внешних зависимостей
# (объктов БД, классов для работы с jwt и т.д)

register_user = Registration()
login_user = Login()
logout_user = Logout()
refresh_tokens = Refresher()
validate_access_token = AccessTokenValidator()
