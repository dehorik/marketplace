import os
from pydantic import EmailStr
from jwt import InvalidTokenError
from typing import Annotated, Dict, Callable
from fastapi import BackgroundTasks, HTTPException, Depends
from fastapi import UploadFile, File, Form, Response, status
from psycopg2.errors import ForeignKeyViolation

from entities.users.models import (
    UserModel,
    AdminModel,
    AdminListModel,
    EmailVerificationModel
)
from auth import (
    AuthorizationService,
    RefreshTokenValidationService,
    PayloadTokenModel,
    RedisClient,
    JWTDecoder,
    get_redis_client,
    get_jwt_decoder
)
from core.tasks import email_verification_task, EmailTokenPayloadModel
from core.database import UserDataAccessObject, get_user_dao
from core.settings import config
from utils import Converter, exists, write_file, delete_file


refresh_token_validation_service = RefreshTokenValidationService()

user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class UserFetchService:
    def __init__(
            self,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(user_dependency)]
    ) -> UserModel:
        user = self.user_data_access_obj.read(payload.sub)
        return self.converter(user)[0]


class UserUpdateService:
    def __init__(
            self,
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.file_writer = file_writer
        self.file_deleter = file_deleter
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[PayloadTokenModel, Depends(user_dependency)],
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

        fields: Dict[str, str | None] = {}

        photo_path = os.path.join(config.USER_CONTENT_PATH, str(payload.sub))
        if photo:
            if not photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            self.file_writer(photo_path, photo.file.read())
            fields["photo_path"] = photo_path
        elif clear_photo:
            if not exists(photo_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="photo does not exist"
                )

            self.file_deleter(photo_path)
            fields["photo_path"] = None

        if username:
            if self.user_data_access_obj.get_user_by_username(username):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="username is already taken"
                )

            fields["username"] = username

        if email:
            background_tasks.add_task(
                email_verification_task,
                payload.sub, email
            )
        elif clear_email:
            fields["email"] = None

        user = self.user_data_access_obj.update(payload.sub, **fields)

        return self.converter(user)[0]


class UserRemovalService:
    def __init__(
            self,
            file_deleter: Callable = delete_file,
            redis_client: RedisClient = get_redis_client(),
            jwt_decoder: JWTDecoder = get_jwt_decoder(),
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel),
    ):
        self.file_delter = file_deleter
        self.redis_client = redis_client
        self.jwt_decoder = jwt_decoder
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            response: Response,
            refresh_token: Annotated[str, Depends(refresh_token_validation_service)]
    ) -> UserModel:
        payload = self.jwt_decoder(refresh_token)
        payload = PayloadTokenModel(**payload)

        admins = self.user_data_access_obj.get_admins(2)
        if len(admins) == 1 and payload.sub == admins[0][0]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="deletion not available"
            )

        response.delete_cookie(config.COOKIE_KEY)
        self.redis_client.delete_user(payload.sub)

        user = self.user_data_access_obj.delete(payload.sub)
        user = self.converter(user)[0]

        if user.photo_path:
            self.file_delter(user.photo_path)

        return user


class EmailVerificationService:
    def __init__(
            self,
            jwt_decoder: JWTDecoder = get_jwt_decoder(),
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(UserModel)
    ):
        self.jwt_decoder = jwt_decoder
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(self, body: EmailVerificationModel) -> UserModel:
        try:
            payload = self.jwt_decoder(body.token)
            payload = EmailTokenPayloadModel(**payload)

            user = self.user_data_access_obj.update(
                user_id=payload.sub,
                email=payload.email
            )

            return self.converter(user)[0]
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
            payload: Annotated[PayloadTokenModel, Depends(superuser_dependency)],
            user_id: Annotated[int, Form(ge=1)],
            role_id: Annotated[int, Form(ge=1)]
    ) -> UserModel:
        if payload.sub == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="you cannot change your role"
            )

        try:
            user = self.user_data_access_obj.set_role(user_id, role_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found"
                )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect role_id"
            )

        return self.converter(user)[0]


class AdminFetchService:
    def __init__(
            self,
            user_dao: UserDataAccessObject = get_user_dao(),
            converter: Converter = Converter(AdminModel)
    ):
        self.user_data_access_obj = user_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(superuser_dependency)]
    ) -> AdminListModel:
        admins = self.user_data_access_obj.get_admins()

        return AdminListModel(
            admins=self.converter(admins)
        )


# dependencies
user_fetch_service = UserFetchService()
user_update_service = UserUpdateService()
user_removal_service = UserRemovalService()
email_verification_service = EmailVerificationService()
role_management_service = RoleManagementService()
admin_fetch_service = AdminFetchService()
