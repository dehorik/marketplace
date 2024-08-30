from fastapi import Response, HTTPException, status

from entities.users.models import UserModel
from core.database import UserDataBase
from utils import Converter
from auth import (
    RedisClient,
    EncodeJWT, DecodeJWT,
    UserCredentialsModel, SuccessfulAuthModel, TokensModel,
    get_password_hash, verify_password
)


class Register:
    def __init__(self, response: Response, credentials: UserCredentialsModel):
        redis = RedisClient()
        user_converter = Converter(UserModel)
        jwt_encoder = EncodeJWT()

        with UserDataBase() as user_db:
            if user_db.get_user_by_user_name(credentials.user_name):
               raise HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail='user_name is already taken'
               )

            user = user_db.create(
                credentials.user_name,
                get_password_hash(credentials.user_password)
            )
            user_model = user_converter.serialization(user)[0]

            access_token_paylaod = {
                "user_id": user_model.user_id,
                "role_id": user_model.role_id,
                "user_name": user_model.user_name
            }
            refresh_token_payload = {
                "user_id": user_model.user_id
            }
            tokens = {
                "access_token": jwt_encoder(access_token_paylaod),
                "refresh_token": jwt_encoder(refresh_token_payload)
            }
            tokens_model = TokensModel(**tokens)

            successful_reg_data = {
                "user": user_model,
                "tokens": tokens_model
            }
            redis.push_token(user_model.user_id, tokens_model.refresh_token)
            response.set_cookie(
                key="refresh_token",
                value=tokens_model.refresh_token
            )
            self.successful_reg_data = SuccessfulAuthModel(**successful_reg_data)


class Login:
    def __init__(self):
        pass
