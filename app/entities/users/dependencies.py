from fastapi import Response, HTTPException, status

from entities.users.models import UserModel
from core.database import UserDataBase
from utils import Converter
from auth import (
    RedisClient,
    CreateTokensModel,
    UserCredentialsModel, SuccessfulAuthModel, TokensModel,
    get_password_hash, verify_password
)


class Register:
    def __init__(self, response: Response, credentials: UserCredentialsModel):
        redis = RedisClient()
        converter = Converter(UserModel)
        tokens_model_creator = CreateTokensModel(TokensModel)

        with UserDataBase() as user_db:
            if user_db.get_user_by_user_name(credentials.user_name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='username is already taken'
                )

            user = user_db.create(
                credentials.user_name,
                get_password_hash(credentials.user_password)
            )
            user_model = converter.serialization(user)[0]

            tokens_model = tokens_model_creator(
                user_model.user_id,
                user_model.role_id,
                user_model.user_name
            )

            redis.push_token(user_model.user_id, tokens_model.refresh_token)
            response.set_cookie(
                key="refresh_token",
                value=tokens_model.refresh_token
            )

            successful_reg_data = {
                "user": user_model,
                "tokens": tokens_model
            }
            self.successful_reg_data = SuccessfulAuthModel(**successful_reg_data)


class Login:
    def __init__(self, response: Response, credentials: UserCredentialsModel):
        redis = RedisClient()
        converter = Converter(UserModel)
        tokens_model_creator = CreateTokensModel(TokensModel)

        with UserDataBase() as user_db:
            user = user_db.get_user_by_user_name(credentials.user_name)

            if not user or not verify_password(credentials.user_password, user[0][3]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect username or password"
                )

            user[0].pop(3)
            user_model = converter.serialization(user)[0]

            tokens_model = tokens_model_creator(
                user_model.user_id,
                user_model.role_id,
                user_model.user_name
            )

            redis.push_token(user_model.user_id, tokens_model.refresh_token)
            response.set_cookie(
                key="refresh_token",
                value=tokens_model.refresh_token
            )

            successful_login_data = {
                "user": user_model,
                "tokens": tokens_model
            }
            self.successful_login_data = SuccessfulAuthModel(**successful_login_data)
