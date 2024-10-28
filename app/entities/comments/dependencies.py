import os
from typing import Annotated, Callable, Dict
from fastapi import Form, UploadFile, HTTPException, File, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.comments.models import (
    CommentModel,
    CommentItemModel,
    CommentItemListModel
)
from auth import AuthorizationService
from core.database import CommentDataAccessObject, get_comment_dao
from core.settings import config
from utils import Converter, exists, write_file, delete_file


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class CommentCreationService:
    def __init__(
            self,
            file_writer: Callable = write_file,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentModel)
    ):
        self.file_writer = file_writer
        self.comment_data_access_obj = comment_dao
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
            has_photo = True if photo else False

            comment = self.comment_data_access_obj.create(
                user_id=user_id,
                product_id=product_id,
                comment_rating=comment_rating,
                comment_text=comment_text,
                has_photo=has_photo
            )
            comment = self.converter.fetchone(comment)

            if photo:
                self.file_writer(comment.photo_path, photo.file.read())

            return comment
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )


class CommentLoaderService:
    """Подгрузка отзывов под товаром"""

    def __init__(
            self,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentItemModel)
    ):
        self.comment_data_access_obj = comment_dao
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

        comments = self.comment_data_access_obj.read(
            product_id=product_id,
            amount=amount,
            last_comment_id=last_comment_id
        )

        return CommentItemListModel(
            comments=self.converter.fetchmany(comments)
        )


class CommentUpdateService:
    def __init__(
            self,
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentModel)
    ):
        self.file_writer = file_writer
        self.file_deleter = file_deleter
        self.comment_data_access_obj = comment_dao
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

        if clear_text and comment_text or clear_photo and photo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conflict between flags and request body"
            )

        fields: Dict[str, str | int | None] = {}

        photo_path = os.path.join(config.COMMENT_CONTENT_PATH, str(comment_id))
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

        if comment_text:
            fields["comment_text"] = comment_text
        elif clear_text:
            fields["comment_text"] = None

        if comment_rating:
            fields["comment_rating"] = comment_rating

        try:
            comment = self.comment_data_access_obj.update(comment_id, **fields)
            comment = self.converter.fetchone(comment)

            return comment
        except ValueError:
            if fields["photo_path"]:
                # если был отправлен запрос на обновление полей
                # несуществующего отзыва, и изображение было записано,
                # то такое изображение необходимо удалить
                self.file_deleter(fields["photo_path"])

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="comment not found"
            )


class CommentRemovalService:
    def __init__(
            self,
            file_deleter: Callable = delete_file,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentModel)
    ):
        self.file_deleter = file_deleter
        self.comment_data_access_obj = comment_dao
        self.converter = converter

    def __call__(self, comment_id: int) -> CommentModel:
        try:
            comment = self.comment_data_access_obj.delete(comment_id)
            comment = self.converter.fetchone(comment)

            if comment.photo_path:
                self.file_deleter(comment.photo_path)

            return comment
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='comment not found'
            )


# dependencies
comment_creation_service = CommentCreationService()
comment_loader_service = CommentLoaderService()
comment_update_service = CommentUpdateService()
comment_removal_service = CommentRemovalService()
