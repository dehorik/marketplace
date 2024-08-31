from typing import Annotated
from fastapi import Response, HTTPException, Depends, status

from auth.redis_client import RedisClient
from auth.tokens import AccessTokenCreator, RefreshTokenCreator
from auth.hashing_psw import get_password_hash, verify_password
from auth.models import TokensModel, UserCredentialsModel, SuccessfulAuthModel
from entities.users.models import UserModel
from core.database import UserDataBase
from utils import Converter


# class BaseDependency:
#     """
#     Базовый класс для других классов-зависимостей,
#     предоставляющий объектам дочерних классов ссылки на экземпляры
#     RedisClient, EncodeJWT и т.д.
#     """
#
#     def __init__(
#             self,
#             redis: RedisClient = RedisClient(),
#             access_token_creator: AccessTokenCreator = AccessTokenCreator(),
#             refresh_token_creator: RefreshTokenCreator = RefreshTokenCreator(),
#             user_database: Annotated[type, UserDataBase] = UserDataBase
#     ):
#         """
#         :param redis: объект для работы с redis
#         :param jwt_encoder: объект для выпуска jwt
#         :param jwt_decoder: объект для расшифровки jwt
#         :param user_database: ссылка на класс для работы с БД (не объект!)
#         """
#
#         self.redis = redis
#         self.jwt_encoder = jwt_encoder
#         self.jwt_decoder = jwt_decoder
#         self.user_database = user_database
#
#         self.tokens_model_creator = CreateTokensModel(TokensModel)
#
#
# class CreateUser(BaseDependency):
#     def __init__(self, converter: Converter = Converter(UserModel)):
#         super().__init__()
#         self.converter = converter
#
#     def __call__(self, credentials: UserCredentialsModel) -> UserModel:
#         with self.user_database() as user_db:
#             if user_db.get_user_by_user_name(credentials.user_name):
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail='username is already taken'
#                 )
#
#             user = user_db.create(
#                 credentials.user_name,
#                 get_password_hash(credentials.user_password)
#             )
#
#             return self.converter.serialization(user)[0]
#
#
# class Register(BaseDependency):
#     def __call__(
#             self,
#             response: Response,
#             user: Annotated[UserModel, Depends(CreateUser())]
#     ) -> SuccessfulAuthModel:
#         tokens = self.tokens_model_creator(
#             user.user_id,
#             user.role_id,
#             user.user_name
#         )
#
#         self.redis.push_token(user.user_id, tokens.refresh_token)
#         response.set_cookie(
#             key="refresh_token",
#             value=tokens.refresh_token
#         )
#
#         successful_reg_data = {
#             "user": user,
#             "tokens": tokens
#         }
#         return SuccessfulAuthModel(**successful_reg_data)
#
#
# class VerifyUserCredentials(BaseDependency):
#     def __init__(self, converter: Converter = Converter(UserModel)):
#         super().__init__()
#         self.converter = converter
#
#     def __call__(self, credentials: UserCredentialsModel) -> UserModel:
#         with self.user_database() as user_db:
#             user = user_db.get_user_by_user_name(credentials.user_name)
#
#             if not user or not verify_password(credentials.user_password, user[0][3]):
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="incorrect username or password"
#                 )
#
#             user[0].pop(3)
#             return self.converter.serialization(user)[0]
#
#
# class Login(BaseDependency):
#     def __call__(
#             self,
#             response: Response,
#             user: Annotated[UserModel, Depends(VerifyUserCredentials())]
#     ) -> SuccessfulAuthModel:
#         tokens = self.tokens_model_creator(
#             user.user_id,
#             user.role_id,
#             user.user_name
#         )
#
#         self.redis.push_token(user.user_id, tokens.refresh_token)
#         response.set_cookie(
#             key="refresh_token",
#             value=tokens.refresh_token
#         )
#
#         successful_login_data = {
#             "user": user,
#             "tokens": tokens
#         }
#         return SuccessfulAuthModel(**successful_login_data)
