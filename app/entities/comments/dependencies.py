from os.path import exists
from typing import Annotated, Type, Callable
from fastapi import Form, UploadFile, HTTPException, File, Path, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.comments.models import (
    CommentModel,
    CommentItemModel,
    CommentItemListModel
)
from core.settings import config
from core.database import CommentDataBase
from utils import Converter, write_file, rewrite_file, delete_file


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            file_writer: Callable = write_file,
            file_rewriter: Callable = rewrite_file,
            file_deleter: Callable = delete_file,
            comment_database: Type[CommentDataBase] = CommentDataBase
    ):
        """
        :param file_writer: ссылка на функцию для записи файлов
        :param file_rewriter: ссылка на функцию для перезаписи файлов
        :param file_deleter: ссылка на функцию для удаления файлов
        :param comment_database: ссылка на класс для работы с БД
        """

        self.file_writer = file_writer
        self.file_rewriter = file_rewriter
        self.file_deleter = file_deleter
        self.comment_database = comment_database


class CommentCreator(BaseDependency):
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
                comment = comment_db.create(
                    user_id=user_id,
                    product_id=product_id,
                    comment_rating=comment_rating,
                    comment_text=comment_text,
                    has_photo=(True if comment_photo else False)
                )

            comment = self.converter.serialization(comment)[0]

            if comment_photo:
                self.file_writer(comment.photo_path, comment_photo.file.read())

            return comment
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect user_id or product_id"
            )


class CommentsLoader(BaseDependency):
    """Подгрузка отзывов под товаром"""

    def __init__(self, converter: Converter = Converter(CommentItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: Annotated[int, Path(ge=1)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_comment_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CommentItemListModel:
        """
        :param product_id: product_id товара
        :param amount: нужное количество отзывов
        :param last_comment_id: comment_id последнего подгруженного отзыва;
               (если это первый запрос на подгрузку отзывов - оставить None)

        :return: список отзывов
        """

        with self.comment_database() as comment_db:
            comments = comment_db.get_comment_item_list(
                product_id=product_id,
                amount=amount,
                last_comment_id=last_comment_id
            )

        return CommentItemListModel(
            comments=self.converter.serialization(comments)
        )


class CommentUpdater(BaseDependency):
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

            if exists(f"..../{photo_path}"):
                self.file_rewriter(photo_path, comment_photo.file.read())
            else:
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

        return self.converter.serialization(comment)[0]


class CommentRewriter(BaseDependency):
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

            if exists(f"..../{photo_path}"):
                self.file_rewriter(photo_path, comment_photo.file.read())
            else:
                self.file_writer(photo_path, comment_photo.file.read())
        else:
            if exists(f"..../{photo_path}"):
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

        return self.converter.serialization(comment)[0]


class CommentDeleter(BaseDependency):
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

        comment = self.converter.serialization(comment)[0]

        if comment.photo_path:
            self.file_deleter(comment.photo_path)

        return comment


# dependencies
create_comment_dependency = CommentCreator()
load_comments_dependency = CommentsLoader()
update_comment_dependency = CommentUpdater()
rewrite_comment_dependency = CommentRewriter()
delete_comment_dependency = CommentDeleter()
