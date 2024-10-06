from os.path import exists
from typing import Annotated, Type, Callable
from fastapi import Form, UploadFile, HTTPException, File, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.comments.models import (
    CommentModel,
    CommentItemModel,
    CommentItemListModel
)
from core.settings import config
from core.database import CommentDataBase
from utils import Converter, write_file, delete_file


class BaseDependency:
    def __init__(
            self,
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file,
            comment_database: Type[CommentDataBase] = CommentDataBase
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
            comment_photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> CommentModel:
        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        try:
            with self.comment_database() as comment_db:
                has_photo = True if comment_photo else False

                comment = comment_db.create(
                    user_id=user_id,
                    product_id=product_id,
                    comment_rating=comment_rating,
                    comment_text=comment_text,
                    has_photo=has_photo
                )

            comment = self.converter(comment)[0]

            if comment_photo:
                self.file_writer(comment.photo_path, comment_photo.file.read())

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
    """
    Обновление отзыва. Соответствует http методу patch,
    обновляет только те поля, для которых были переданы значения
    """

    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            comment_id: int,
            comment_rating: Annotated[
                int | None, Form(ge=1, le=5)
            ] = None,
            comment_text: Annotated[
                str | None, Form(min_length=2, max_length=100)
            ] = None,
            comment_photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> CommentModel:
        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            photo_path = f"{config.COMMENT_CONTENT_PATH}/{comment_id}"
            self.file_writer(photo_path, comment_photo.file.read())
        else:
            photo_path = None

        fields_for_update = {
            key: value
            for key, value in {
                "comment_rating": comment_rating,
                "comment_text": comment_text,
                "photo_path": photo_path
            }.items()
            if value
        }

        with self.comment_database() as comment_db:
            comment = comment_db.update(
                comment_id=comment_id,
                **fields_for_update
            )

        if not comment:
            if photo_path:
                self.file_deleter(photo_path)

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect comment_id"
            )

        return self.converter(comment)[0]


class CommentRewritingService(BaseDependency):
    """
    Обновление отзыва. Соответствует http методу put,
    обновляет все поля отзыва.
    """

    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            comment_id: int,
            comment_rating: Annotated[
                int, Form(ge=1, le=5)
            ],
            comment_text: Annotated[
                str | None, Form(min_length=2, max_length=100)
            ] = None,
            comment_photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> CommentModel:
        """
        Если для какого-то из полей не будет передано значение,
        то это поле перезапишется со значением null
        """

        photo_path = f"{config.COMMENT_CONTENT_PATH}/{comment_id}"

        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            self.file_writer(photo_path, comment_photo.file.read())
        else:
            if exists(f"../{photo_path}"):
                self.file_deleter(photo_path)
                photo_path = None

        with self.comment_database() as comment_db:
            comment = comment_db.update(
                comment_id=comment_id,
                comment_rating=comment_rating,
                comment_text=comment_text,
                photo_path=photo_path
            )

        if not comment:
            if photo_path:
                self.file_deleter(photo_path)

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
comment_rewriting_service = CommentRewritingService()
comment_removal_service = CommentRemovalService()
