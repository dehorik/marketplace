from pydantic import BaseModel, Field

from entities.users.models import UserModel


class TokensModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UserCredentialsModel(BaseModel):
    user_name: str = Field(min_length=6, max_length=14)
    user_password: str = Field(min_length=8, max_length=18)


class SuccessfulAuthModel(BaseModel):
    user: UserModel
    tokens: TokensModel
