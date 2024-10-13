from os.path import exists
from typing import Annotated, Type, Callable, Dict
from fastapi import Form, UploadFile, HTTPException, File, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.comments.models import (
    CommentModel,
    CommentItemModel,
    CommentItemListModel
)
from auth import PayloadTokenModel, AuthorizationService
from core.settings import config
from core.database import CommentDAO
from utils import Converter, write_file, delete_file


base_user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
owner_dependency = AuthorizationService(min_role_id=3)


class BaseDependency:
    def __init__(
            self,
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file,
            comment_database: Type[CommentDAO] = CommentDAO
    ):
        """
        :param file_writer: ссылка на функцию для записи и перезаписи файлов
        :param file_deleter: ссылка на функцию для удаления файлов
        :param comment_database: ссылка на класс для работы с БД
        """

        self.file_writer = file_writer
        self.file_deleter = file_deleter
        self.comment_database = comment_database


class CommentCreationService(BaseDependency):
    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            user_id: int,
            product_id: int,
            comment_rating: Annotated[
                int, Form(ge=1, le=5)
            ],
            comment_text: Annotated[
                str | None, Form(min_length=2, max_length=100)
            ] = None,
            photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> CommentModel:
        if photo:
            if not photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        try:
            with self.comment_database() as comment_db:
                has_photo = True if photo else False

                comment = comment_db.create(
                    user_id=user_id,
                    product_id=product_id,
                    comment_rating=comment_rating,
                    comment_text=comment_text,
                    has_photo=has_photo
                )

            comment = self.converter(comment)[0]

            if photo:
                self.file_writer(comment.photo_path, photo.file.read())

            return comment
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect user_id or product_id"
            )


class CommentLoaderService(BaseDependency):
    """Подгрузка отзывов под товаром"""

    def __init__(self, converter: Converter = Converter(CommentItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: Annotated[int, Query(ge=1)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_comment_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CommentItemListModel:
        """
        :param product_id: product_id товара
        :param amount: нужное количество отзывов
        :param last_comment_id: comment_id последнего подгруженного отзыва;
               (если это первый запрос на подгрузку отзывов - оставить None)
        """

        with self.comment_database() as comment_db:
            comments = comment_db.read(
                product_id=product_id,
                amount=amount,
                last_comment_id=last_comment_id
            )

        return CommentItemListModel(
            comments=self.converter(comments)
        )


class CommentUpdateService(BaseDependency):
    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            comment_id: int,

            clear_text: Annotated[bool, Form()] = False,
            clear_photo: Annotated[bool, Form()] = False,

            comment_rating: Annotated[
                int | None, Form(ge=1, le=5)
            ] = None,
            comment_text: Annotated[
                str | None, Form(min_length=2, max_length=100)
            ] = None,
            photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> CommentModel:
        """
        :param comment_id: id отзыва

        :param clear_text: флаг очистки поля с текстом
        :param clear_photo: флаг удаления фотографии

        :param comment_rating: рейтинг для обновления
        :param comment_text: текст отзыва для обновления
        :param photo: фото к отзыву для записи или перезаписи

        ВАЖНО
        Флаги используются для того, чтобы указать те поля, значения из
        которых нужно удалить. Одновременная передача значения true во флаг и
        отправка данных для соответствующего поля приведет к ошибке.
        """

        if photo:
            if not photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        if clear_text and comment_text or clear_photo and photo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="conflict between flags and request body"
            )

        fields_for_update: Dict[str, str | int | None] = {}

        if comment_rating:
            fields_for_update["comment_rating"] = comment_rating

        if comment_text:
            fields_for_update["comment_text"] = comment_text
        elif clear_text:
            fields_for_update["comment_text"] = None

        if photo:
            photo_path = f"{config.COMMENT_CONTENT_PATH}/{comment_id}"
            self.file_writer(photo_path, photo.file.read())
            fields_for_update["photo_path"] = photo_path
        elif clear_photo:
            photo_path = f"{config.COMMENT_CONTENT_PATH}/{comment_id}"

            if not exists(f"../{photo_path}"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="photo does not exist"
                )

            self.file_deleter(photo_path)
            fields_for_update["photo_path"] = None

        with self.comment_database() as commend_db:
            comment = commend_db.update(
                comment_id=comment_id,
                **fields_for_update
            )

        if not comment:
            if fields_for_update["photo_path"]:
                self.file_deleter(fields_for_update["photo_path"])

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect comment_id"
            )

        return self.converter(comment)[0]


class CommentRemovalService(BaseDependency):
    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, comment_id: int) -> CommentModel:
        with self.comment_database() as comment_db:
            comment = comment_db.delete(comment_id)

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect comment_id'
            )

        comment = self.converter(comment)[0]

        if comment.photo_path:
            self.file_deleter(comment.photo_path)

        return comment


# dependencies
comment_creation_service = CommentCreationService()
comment_loader_service = CommentLoaderService()
comment_update_service = CommentUpdateService()
comment_removal_service = CommentRemovalService()
