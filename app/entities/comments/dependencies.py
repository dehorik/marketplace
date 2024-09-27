from typing import Annotated, Type, Callable
from fastapi import Form, UploadFile, HTTPException, status, File
from psycopg2.errors import ForeignKeyViolation

from entities.comments.models import (
    CommentModel,
    CommentItemModel,
    CommentItemListModel
)
from core.settings import config
from core.database import CommentDataBase
from utils import write_file, rewrite_file, delete_file, Converter


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            file_writer: Callable = write_file,
            file_rewriter: Callable = rewrite_file,
            file_deleter: Callable = delete_file,
            comment_database: Type[CommentDataBase] = CommentDataBase
    ):
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
                int,
                Form(ge=1, le=5)
            ],
            comment_text: Annotated[
                str | None,
                Form(min_length=2, max_length=100)
            ] = None,
            comment_photo: Annotated[
                UploadFile,
                File()
            ] = None
    ) -> CommentModel:
        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            comment_photo_path = self.file_writer(
                config.COMMENT_PHOTO_PATH,
                comment_photo.file.read()
            )
        else:
            comment_photo_path = None

        try:
            with self.comment_database() as comment_db:
                comment = comment_db.create(
                    user_id,
                    product_id,
                    comment_rating,
                    comment_text,
                    comment_photo_path
                )
        except ForeignKeyViolation:
            if comment_photo_path:
                self.file_deleter(comment_photo_path)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="incorrect user_id or product_id"
            )

        return self.converter.serialization(comment)[0]


class CommentLoader(BaseDependency):
    """Подгрузка отзывов под товаром"""

    def __init__(self, converter: Converter = Converter(CommentItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: int,
            amount: int = 12,
            last_comment_id: int | None = None
    ) -> CommentItemListModel:
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
    """Обновление отзыва"""

    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            comment_id: int,

            del_text: bool = False,
            del_photo: bool = False,

            comment_text: Annotated[
                str | None,
                Form(min_length=3, max_length=200)
            ] = None,
            comment_rating: Annotated[
                int | None,
                Form(ge=1, le=5)
            ] = None,
            comment_photo: Annotated[
                UploadFile,
                File()
            ] = None
    ) -> CommentModel:
        """
        :param comment_id: id отзыва (параметр пути)

        параметры del_text и del_photo указывают на то, нужно ли
        удалить уже существующие текст и фото под отзывом;
        попытка передать true в один из этих параметров
        параллельно с передачей соответствующх значений в форме
        приведёт к ошибке!

        :param del_text: удалять ли существующий текст
        :param del_photo: удалять ли существующее фото

        :param comment_text: текст под отзывом;
               (при замене или первичной установке)
        :param comment_rating: рейтинг
        :param comment_photo: фотография под отзывом;
               (при замене существующей или первичной установке)

        :return: отредактированный отзыв
        """

        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        if del_text and comment_text or del_photo and comment_photo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="conflict between query params and form data"
            )

        fields_for_update = {
            key: value
            for key, value in {
                "comment_text": comment_text,
                "comment_rating": comment_rating
            }.items()
            if value
        }

        if del_text:
            fields_for_update["comment_text"] = None

        with self.comment_database() as comment_db:
            comment = comment_db.update(
                comment_id=comment_id,
                **fields_for_update
            )

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect comment_id'
            )

        comment = self.converter.serialization(comment)[0]

        if comment_photo:
            if comment.comment_photo_path:
                self.file_rewriter(
                    comment.comment_photo_path,
                    comment_photo.file.read()
                )
            else:
                comment_photo_path = self.file_writer(
                    config.COMMENT_PHOTO_PATH,
                    comment_photo.file.read()
                )

                with self.comment_database() as comment_db:
                    comment = comment_db.update(
                        comment_id=comment_id,
                        comment_photo_path=comment_photo_path
                    )

                comment = self.converter.serialization(comment)[0]

        elif del_photo:
            if not comment.comment_photo_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="this comment does not have a photo"
                )

            self.file_deleter(comment.comment_photo_path)

            with self.comment_database() as comment_db:
                comment = comment_db.update(
                    comment_id=comment_id,
                    comment_photo_path=None
                )

            comment = self.converter.serialization(comment)[0]

        return comment


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

        if comment.comment_photo_path:
            self.file_deleter(comment.comment_photo_path)

        return comment


# dependencies
create_comment_dependency = CommentCreator()
load_comments_dependency = CommentLoader()
update_comment_dependency = CommentUpdater()
delete_comment_dependency = CommentDeleter()
