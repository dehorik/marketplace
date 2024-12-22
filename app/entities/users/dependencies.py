import os
from pydantic import EmailStr
from typing import Annotated, Callable
from jwt import InvalidTokenError
from fastapi import UploadFile, File, Form, Query
from fastapi import BackgroundTasks, HTTPException, Depends,  Response, status
from psycopg2.errors import ForeignKeyViolation, RaiseException

from entities.users.models import (
    UserModel,
    EmailVerificationRequest,
    SetRoleRequest,
    UserItemModel,
    UserItemListModel
)
from auth import (
    AuthorizationService,
    TokenPayloadModel,
    RedisClient,
    JWTDecoder,
    NonExistentUserError,
    get_redis_client,
    get_jwt_decoder
)
from core.tasks import (
    email_verification_task,
    comments_removal_task,
    orders_removal_task,
    EmailTokenPayloadModel
)
from core.database import UserDataAccessObject, get_user_dao
from core.settings import config
from utils import Converter, write_file, delete_file


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class FetchUserService:
    def __init__(
            self,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)]
    ) -> UserModel:
        try:
            user = self.user_data_access_obj.read(payload.sub)
            user = self.converter.fetchone(user)

            return user
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )


class UserUpdateService:
    def __init__(
            self,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel),
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file
    ):
        self.user_data_access_obj = user_dao
        self.converter = converter
        self.file_writer = file_writer
        self.file_deleter = file_deleter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            clear_email: Annotated[bool, Form()] = False,
            clear_photo: Annotated[bool, Form()] = False,
            username: Annotated[str, Form(min_length=6, max_length=16)] = None,
            email: Annotated[EmailStr, Form()] = None,
            photo: Annotated[UploadFile, File()] = None
    ) -> UserModel:
        if clear_email and email or clear_photo and photo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conflict between flags and request body"
            )

        if photo:
            if not check_file(photo):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            photo_path = os.path.join(config.USER_CONTENT_PATH, str(payload.sub))
        else:
            photo_path = None

        try:
            user = self.user_data_access_obj.update(
                user_id=payload.sub,
                clear_email=clear_email,
                clear_photo=clear_photo,
                username=username,
                photo_path=photo_path
            )
            user = self.converter.fetchone(user)

            if photo:
                self.file_writer(user.photo_path, photo.file.read())
            elif clear_photo:
                self.file_deleter(os.path.join(config.USER_CONTENT_PATH, str(payload.sub)))

            if email:
                background_tasks.add_task(
                    email_verification_task,
                    payload.sub, email, user.username
                )

            return user
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="username is already taken"
            )


class EmailVerificationService:
    """Привязка почты к аккаунту"""

    def __init__(
            self,
            jwt_decoder: JWTDecoder = get_jwt_decoder(),
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.jwt_decoder = jwt_decoder
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(self, data: EmailVerificationRequest) -> UserModel:
        try:
            payload = self.jwt_decoder(data.token)

            if not payload.get("email"):
                raise InvalidTokenError

            payload = EmailTokenPayloadModel(**payload)

            user = self.user_data_access_obj.update(
                user_id=payload.sub,
                email=payload.email
            )
            user = self.converter.fetchone(user)

            return user
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid token"
            )


class RoleManagementService:
    """Управление ролями пользователей"""

    def __init__(
            self,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(superuser_dependency)],
            data: SetRoleRequest
    ) -> UserModel:
        if payload.sub == data.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you cannot change your role"
            )

        try:
            user = self.user_data_access_obj.update(
                user_id=data.user_id,
                role_id=data.role_id
            )
            user = self.converter.fetchone(user)

            return user
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect role_id"
            )


class UserDeletionService:
    def __init__(
            self,
            jwt_decoder: JWTDecoder = get_jwt_decoder(),
            redis_client: RedisClient = get_redis_client(),
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel),
            file_deleter: Callable = delete_file
    ):
        self.jwt_decoder = jwt_decoder
        self.redis_client = redis_client
        self.user_data_access_obj = user_dao
        self.converter = converter
        self.file_deleter = file_deleter

    def __call__(
            self,
            response: Response,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)]
    ) -> UserModel:
        try:
            self.redis_client.delete_user(payload.sub)
            response.delete_cookie(config.REFRESH_COOKIE_KEY)
            response.delete_cookie(config.USER_ID_COOKIE_KEY)

            user = self.user_data_access_obj.delete(payload.sub)
            user = self.converter.fetchone(user)

            background_tasks.add_task(comments_removal_task)
            background_tasks.add_task(orders_removal_task)

            if user.photo_path:
                self.file_deleter(user.photo_path)

            return user
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="at least one superuser is required"
            )
        except NonExistentUserError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="not authenticated"
            )


class FetchUsersService:
    def __init__(
            self,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserItemModel)
    ):
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(superuser_dependency)],
            min_role_id: Annotated[int, Query(ge=1)] = 2
    ) -> UserItemListModel:
        users = self.user_data_access_obj.get_users(min_role_id=min_role_id)
        users = self.converter.fetchmany(users)

        return UserItemListModel(users=users)


def check_file(file: UploadFile) -> bool:
    return file.content_type.split('/')[0] == 'image'


fetch_user_service = FetchUserService()
user_update_service = UserUpdateService()
email_verification_service = EmailVerificationService()
role_management_service = RoleManagementService()
user_deletion_service = UserDeletionService()
fetch_users_service = FetchUsersService()
