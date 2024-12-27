import os
from datetime import datetime, timezone
from typing import Annotated, Callable
from fastapi import Depends, HTTPException, Form, UploadFile, File, Query, Path, status
from psycopg2.errors import ForeignKeyViolation, RaiseException

from entities.comments.models import (
    CommentModel,
    CommentItemModel,
    CommentItemListModel
)
from auth import AuthorizationService, TokenPayloadModel
from core.database import CommentDataAccessObject, get_comment_dao
from core.settings import config
from utils import Converter, write_file, delete_file, exists


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class CommentCreationService:
    def __init__(
            self,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentModel),
            file_writer: Callable = write_file
    ):
        self.comment_data_access_obj = comment_dao
        self.converter = converter
        self.file_writer = file_writer

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            product_id: Annotated[int, Form(ge=1)],
            rating: Annotated[int, Form(ge=1, le=5)],
            text: Annotated[str | None, Form(min_length=2, max_length=200)] = None,
            photo: Annotated[UploadFile | None, File()] = None
    ) -> CommentModel:
        if photo:
            if not check_file(photo):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        try:
            comment = self.comment_data_access_obj.create(
                user_id=payload.sub,
                product_id=product_id,
                rating=rating,
                current_date=datetime.now(timezone.utc).date(),
                text=text,
                has_photo=bool(photo)
            )
            comment = self.converter.fetchone(comment)

            if photo:
                self.file_writer(comment.photo_path, photo.file.read())

            return comment
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )


class FetchCommentsService:
    """Получение отзывов под товаром"""

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
            amount: Annotated[int, Query(ge=0)] = 15,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CommentItemListModel:
        """
        :param product_id: id товара
        :param amount: нужное количество отзывов
        :param last_id: comment_id последнего подгруженного отзыва;
               (если это первый запрос на подгрузку отзывов - оставить None)
        """

        comments = self.comment_data_access_obj.read(
            product_id=product_id,
            amount=amount,
            last_id=last_id
        )
        comments = self.converter.fetchmany(comments)

        return CommentItemListModel(comments=comments)


class CommentUpdateService:
    def __init__(
            self,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentModel),
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file
    ):
        self.comment_data_access_obj = comment_dao
        self.converter = converter
        self.file_writer = file_writer
        self.file_deleter = file_deleter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            comment_id: Annotated[int, Path(ge=1)],
            clear_text: Annotated[bool, Form()] = False,
            clear_photo: Annotated[bool, Form()] = False,
            rating: Annotated[int | None, Form(ge=1, le=5)] = None,
            text: Annotated[str | None, Form(min_length=2, max_length=200)] = None,
            photo: Annotated[UploadFile | None, File()] = None
    ) -> CommentModel:
        """
        :param comment_id: id отзыва
        :param clear_text: флаг очистки поля с текстом
        :param clear_photo: флаг удаления фотографии
        :param rating: рейтинг для обновления
        :param text: текст отзыва для обновления
        :param photo: фото к отзыву для записи или перезаписи

        Флаги используются для того, чтобы указать те поля, значения из
        которых нужно удалить. Одновременная передача значения true во флаг и
        отправка данных для соответствующего поля приведет к ошибке.
        """
        if clear_text and text or clear_photo and photo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conflict between flags and form data"
            )

        if photo:
            if not check_file(photo):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            photo_path = os.path.join(
                config.COMMENT_CONTENT_PATH,
                str(comment_id)
            )
        else:
            photo_path = None

        try:
            comment = self.comment_data_access_obj.update(
                comment_id=comment_id,
                user_id=payload.sub,
                current_date=datetime.now(timezone.utc).date(),
                clear_text=clear_text,
                clear_photo=clear_photo,
                rating=rating,
                text=text,
                photo_path=photo_path
            )
            comment = self.converter.fetchone(comment)

            if photo:
                self.file_writer(comment.photo_path, photo.file.read())
            elif clear_photo:
                photo_path = os.path.join(
                    config.COMMENT_CONTENT_PATH,
                    str(comment_id)
                )

                if exists(photo_path):
                    self.file_deleter(photo_path)

            return comment
        except (ValueError, RaiseException):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="comment not found"
            )


class CommentDeletionService:
    def __init__(
            self,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            converter: Converter = Converter(CommentModel),
            file_deleter: Callable = delete_file
    ):
        self.comment_data_access_obj = comment_dao
        self.converter = converter
        self.file_deleter = file_deleter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            comment_id: Annotated[int, Path(ge=1)]
    ) -> CommentModel:
        try:
            comment = self.comment_data_access_obj.delete(comment_id, payload.sub)
            comment = self.converter.fetchone(comment)

            if comment.photo_path:
                self.file_deleter(comment.photo_path)

            return comment
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='comment not found'
            )


def check_file(file: UploadFile) -> bool:
    return file.content_type.split('/')[0] == 'image'


comment_creation_service = CommentCreationService()
fetch_comments_service = FetchCommentsService()
comment_update_service = CommentUpdateService()
comment_deletion_service = CommentDeletionService()
