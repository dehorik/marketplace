from fastapi import HTTPException, status

from auth.models import Credentials
from core.database import Session, UserDataBase
from entities.users.models import UserModel
from utils import Converter


class Register:
    def __init__(self, credentials: Credentials):
        converter = Converter(UserModel)
        session = Session()
        user_db = UserDataBase(session)

        if not user_db.check_user_name(credentials.user_name):
            user_db.close()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='user_name is already taken!'
            )

        user = user_db.create(credentials.user_name, credentials.user_password)
        user_db.close()
        self.user = converter.serialization(user)[0]
