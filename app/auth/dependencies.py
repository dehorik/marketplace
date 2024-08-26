from fastapi import HTTPException, status

from auth.security import HashPassword
from auth.models import Credentials
from core.database import Session, UserDataBase
from entities.users.models import UserModel
from utils import Converter


class Register:
    def __init__(self, credentials: Credentials):
        hash_psw = HashPassword()
        converter = Converter(UserModel)
        session = Session()
        user_db = UserDataBase(session)

        if not user_db.check_user_name(credentials.user_name):
            user_db.close()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='user_name is already taken!'
            )

        user = user_db.create(
            credentials.user_name,
            hash_psw(credentials.user_password)
        )
        user_db.close()
        self.user = converter.serialization(user)[0]


class Login:
    def __init__(self, credentials: Credentials):
        hash_psw = HashPassword()
        converter = Converter(UserModel)
        session = Session()
        user_db = UserDataBase(session)

        user = user_db.login_user(
            credentials.user_name,
            hash_psw(credentials.user_password)
        )
        if not user:
            user_db.close()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='incorrect user_name or user_password'
            )

        user_db.close()
        self.user = converter.serialization(user)
