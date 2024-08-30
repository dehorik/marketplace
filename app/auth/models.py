from pydantic import BaseModel, Field

from entities.users.models import UserModel


class TokensModel(BaseModel):
    refresh_token: str
    access_token: str


class UserCredentialsModel(BaseModel):
    user_name: str = Field(min_length=6, max_length=14)
    user_password: str = Field(min_length=8, max_length=18)


class SuccessfulAuthModel(BaseModel):
    user: UserModel
    tokens: TokensModel
