from fastapi import HTTPException, Response, status, Cookie

from auth.redis_client import ManageSessionsDataBase
from auth.tools import HashPassword, SessionIdGenerator
from auth.models import Credentials
from core.database import Session, UserDataBase
from entities.users.models import UserModel
from utils import Converter


class Register:
    def __init__(self, credentials: Credentials, response: Response):
        session_id_generator = SessionIdGenerator()
        hash_psw = HashPassword()
        converter = Converter(UserModel)
        session = Session()
        user_db = UserDataBase(session)
        session_db = ManageSessionsDataBase(session)

        if not user_db.check_user_name(credentials.user_name):
            user_db.close()
            session_db.close()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='user_name is already taken!'
            )

        user = user_db.create(
            credentials.user_name,
            hash_psw(credentials.user_password)
        )

        session_key = session_id_generator()
        session_db.set_session(session_key, user[0][0])
        response.set_cookie(
            'session-id',
            session_key,
            httponly=True,
            max_age=15638400
        )

        user_db.close()
        session_db.close()
        self.user = converter.serialization(user)[0]


class Login:
    def __init__(self, credentials: Credentials, response: Response):
        session_id_generator = SessionIdGenerator()
        hash_psw = HashPassword()
        converter = Converter(UserModel)
        session = Session()
        user_db = UserDataBase(session)
        session_db = ManageSessionsDataBase(session)

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

        session_key = session_id_generator()
        session_db.set_session(session_key, user[0][0])
        response.set_cookie(
            'session-id',
            session_key,
            httponly=True,
            max_age=15638400
        )

        user_db.close()
        session_db.close()
        self.user = converter.serialization(user)


class CookieLogin:
    def __init__(self, session_key: str = Cookie(alias='session-id')):
        converter = Converter(UserModel)
        session = Session()
        session_db = ManageSessionsDataBase(session)

        user = session_db.get_user_by_session_key(session_key)
        if not user:
            session_db.close()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid session-id'
            )

        self.user = converter.serialization(user)


class CookieLoginOut:
    def __init__(self, response: Response, session_key: str = Cookie(alias='session-id')):
        session = Session()
        session_db = ManageSessionsDataBase(session)

        session_data = session_db.delete_session(session_key)
        if not session_data:
            session_db.close()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='invalid session-id'
            )

        response.delete_cookie('session-id')
        session_db.close()
