from typing import Annotated
from fastapi import Response, HTTPException, status

from entities.users.models import UserModel
from core.database import UserDataBase
from utils import Converter
from auth import (
    RedisClient,
    EncodeJWT, DecodeJWT,
    CreateTokensModel, UserCredentialsModel, SuccessfulAuthModel, TokensModel,
    get_password_hash, verify_password
)


class BaseDependency:
    """
    Базовый класс для других классов-зависимостей,
    предоставляющий объектам дочерних классов ссылки на экземпляры
    RedisClient, UserDataBase и т.д.
    """

    def __init__(
            self,
            redis: RedisClient = RedisClient(),
            jwt_encoder: EncodeJWT = EncodeJWT(),
            jwt_decoder: DecodeJWT = DecodeJWT(),
            database: Annotated[type, UserDataBase] = UserDataBase
    ):
        """
        :param redis: объект для работы с redis
        :param jwt_encoder: объект для выпуска jwt
        :param jwt_decoder: объект для расшифровки jwt
        :param database: ссылка на класс для работы с БД (не объект!)
        """

        self.redis = redis
        self.jwt_encoder = jwt_encoder
        self.jwt_decoder = jwt_decoder
        self.database = database

        self.tokens_model_creator = CreateTokensModel(TokensModel)


class Register(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            response: Response,
            credentials: UserCredentialsModel
    ) -> SuccessfulAuthModel:
        with self.database() as user_db:
            if user_db.get_user_by_user_name(credentials.user_name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='username is already taken'
                )

            user = user_db.create(
                credentials.user_name,
                get_password_hash(credentials.user_password)
            )
            user_model = self.converter.serialization(user)[0]

            tokens_model = self.tokens_model_creator(
                user_model.user_id,
                user_model.role_id,
                user_model.user_name
            )

            self.redis.push_token(user_model.user_id, tokens_model.refresh_token)
            response.set_cookie(
                key="refresh_token",
                value=tokens_model.refresh_token
            )

            successful_reg_data = {
                "user": user_model,
                "tokens": tokens_model
            }

            return SuccessfulAuthModel(**successful_reg_data)


class Login(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            response: Response,
            credentials: UserCredentialsModel
    ) -> SuccessfulAuthModel:
        with self.database() as user_db:
            user = user_db.get_user_by_user_name(credentials.user_name)

            if not user or not verify_password(credentials.user_password, user[0][3]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect username or password"
                )

            user[0].pop(3)
            user_model = self.converter.serialization(user)[0]

            tokens_model = self.tokens_model_creator(
                user_model.user_id,
                user_model.role_id,
                user_model.user_name
            )

            self.redis.push_token(user_model.user_id, tokens_model.refresh_token)
            response.set_cookie(
                key="refresh_token",
                value=tokens_model.refresh_token
            )

            successful_login_data = {
                "user": user_model,
                "tokens": tokens_model
            }

            return SuccessfulAuthModel(**successful_login_data)
