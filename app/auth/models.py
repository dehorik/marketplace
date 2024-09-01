from fastapi import Form
from pydantic import BaseModel

from entities.users.models import UserModel


class UserCredentialsModel(BaseModel):
    user_name: str = Form(min_length=6, max_length=14)
    user_password: str = Form(min_length=8, max_length=18)


class AccessTokenModel(BaseModel):
    access_token: str
    type: str = "Bearer"


class AuthorizationModel(BaseModel):
    user: UserModel
    access_token: AccessTokenModel
