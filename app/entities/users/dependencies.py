import os
from pydantic import EmailStr
from typing import Type, Annotated, Dict, Callable
from fastapi import BackgroundTasks, Depends, HTTPException, Form, UploadFile, File, status
from psycopg2.errors import ForeignKeyViolation

from entities.users.models import UserModel
from auth import PayloadTokenModel, AuthorizationService
from core.settings import config
from core.database import UserDAO
from core.tasks import email_sending_service
from utils import Converter, exists, write_file, delete_file


base_user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
owner_dependency = AuthorizationService(min_role_id=3)


class BaseDependency:
    def __init__(
            self,
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file,
            user_database: Type[UserDAO] = UserDAO
    ):
        """
        :param file_writer: ссылка на функцию для записи и перезаписи файлов
        :param file_deleter: ссылка на функцию для удаления файлов
        :param user_database: ссылка на класс для работы с БД
        """

        self.file_writer = file_writer
        self.file_deleter = file_deleter
        self.user_database = user_database


class UserDataGettingService(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)]
    ) -> UserModel:
        with self.user_database() as user_db:
            user = user_db.read(payload.sub)

        return self.converter(user)[0]


class UserDataUpdateService(BaseDependency):
    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],

            clear_email: Annotated[bool, Form()] = False,
            clear_photo: Annotated[bool, Form()] = False,

            username: Annotated[str, Form(min_length=6, max_length=16)] = None,
            email: Annotated[EmailStr, Form()] = None,
            photo: Annotated[UploadFile, File()] = None
    ) -> UserModel:
        if photo:
            if not photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        if clear_email and email or clear_photo and photo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="conflict between flags and request body"
            )

        user_db = self.user_database()

        fields_for_update: Dict[str, str | None] = {}

        if username:
            if user_db.get_user_by_username(username):
                user_db.close()

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="username is already taken"
                )

            fields_for_update["username"] = username

        if email:
            background_tasks.add_task(
                email_sending_service,
                payload.sub, email
            )
            fields_for_update["email"] = email
        elif clear_email:
            fields_for_update["email"] = None

        if photo:
            photo_path = os.path.join(
                config.USER_CONTENT_PATH,
                str(payload.sub)
            )
            self.file_writer(photo_path, photo.file.read())
            fields_for_update["photo_path"] = photo_path
        elif clear_photo:
            photo_path = os.path.join(
                config.USER_CONTENT_PATH,
                str(payload.sub)
            )

            if not exists(photo_path):
                user_db.close()

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="photo does not exist"
                )

            self.file_deleter(photo_path)
            fields_for_update["photo_path"] = None

        user = user_db.update(
            user_id=payload.sub,
            **fields_for_update
        )
        user_db.close()

        return self.converter(user)[0]


class EmailVerificationService(BaseDependency):
    def __call__(self) -> dict:
        pass


class RoleUpdateService(BaseDependency):
    """Управление ролями пользователей"""

    def __init__(self, converter: Converter = Converter(UserModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(owner_dependency)],
            user_id: Annotated[int, Form(ge=1)],
            role_id: Annotated[int, Form(ge=1)]
    ) -> UserModel:
        if payload.sub == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="you cannot change your role"
            )

        try:
            with self.user_database() as user_db:
                user = user_db.set_role(user_id, role_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="incorrect user_id"
                )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect role_id"
            )

        return self.converter(user)[0]


# dependencies
user_data_getting_service = UserDataGettingService()
user_data_update_service = UserDataUpdateService()
email_verification_service = EmailVerificationService()
role_update_service = RoleUpdateService()
