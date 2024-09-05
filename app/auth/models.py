from fastapi import Form
from pydantic import BaseModel
from datetime import datetime

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


class PayloadTokenModel(BaseModel):
    token_type: str
    user_id: int
    role_id: int
    user_name: str


class FullPayloadTokenModel(BaseModel):
    token_type: str
    sub: int
    user_id: int
    role_id: int
    user_name: str
    iat: datetime
    exp: datetime


class LogoutModel(BaseModel):
    message: str = 'successful logout'
