from typing import Annotated, Type
from fastapi import Form, UploadFile, HTTPException, status

from entities.comments.models import (
    CommentModel,
    CommentItemListModel,
    CommentItemModel
)
from core.settings import config
from core.database import CommentDataBase
from utils import FileWriter, FileReWriter, FileDeleter, Converter


class BaseDependency:
    """
    Базовый класс для других классов-зависимостей,
    предоставляющий объектам дочерних классов ссылки на экземпляры
    FileDeleter, CommentDataBase и т.д.
    """

    def __init__(
            self,
            file_writer: Type[FileWriter] = FileWriter,
            file_rewriter: Type[FileReWriter] = FileReWriter,
            file_deleter: Type[FileDeleter] = FileDeleter,
            comment_database: Type[CommentDataBase] = CommentDataBase
    ):
        self.file_writer = file_writer
        self.file_rewriter = file_rewriter
        self.file_deleter = file_deleter
        self.comment_database = comment_database


class CreateComment(BaseDependency):
    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            user_id: int,
            product_id: int,
            comment_rating: Annotated[int, Form(ge=1, le=5)],
            comment_text: Annotated[str | None, Form(min_length=3, max_length=200)] = None,
            comment_photo: UploadFile | None = None
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
            ).path
        else:
            comment_photo_path = None

        with self.comment_database() as comment_db:
            comment = comment_db.create(
                user_id,
                product_id,
                comment_rating,
                comment_text,
                comment_photo_path
            )

            return self.converter.serialization(comment)[0]


class CommentList(BaseDependency):
    def __init__(self, converter: Converter = Converter(CommentItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: int,
            amount: int,
            last_comment_id: int | None = None
    ) -> CommentItemListModel:
        with self.comment_database() as comment_db:
            comments = comment_db.get_comment_item_list(
                product_id,
                amount,
                last_comment_id
            )

            return CommentItemListModel(
                comments=self.converter.serialization(comments)
            )


class UpdateComment(BaseDependency):
    def __init__(self, converter: Converter = Converter(CommentModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            comment_id: int,
            comment_text: Annotated[str | None, Form(min_length=3, max_length=200)] = None,
            comment_rating: Annotated[int | None, Form(ge=1, le=5)] = None,
            comment_photo: UploadFile | None = None
    ) -> CommentModel:
        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        with self.comment_database() as comment_db:
            params = {
                "comment_text": comment_text,
                "comment_rating": comment_rating
            }
            params = {key: value for key, value in params.items() if value is not None}
            comment = comment_db.update(comment_id, **params)

            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='incorrect comment_id'
                )

            if comment_photo:
                comment_photo_path = comment[0][-1]

                if comment_photo_path:
                    self.file_rewriter(
                        comment_photo_path,
                        comment_photo.file.read()
                    )
                else:
                    comment_photo_path = self.file_writer(
                        config.COMMENT_PHOTO_PATH,
                        comment_photo.file.read()
                    ).path

                    comment = comment_db.update(
                        comment_id,
                        comment_photo_path=comment_photo_path
                    )

            return self.converter.serialization(comment)[0]


class DeleteComment(BaseDependency):
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

            deleted_comment_photo_path = comment[0][-1]
            if deleted_comment_photo_path:
                self.file_deleter(deleted_comment_photo_path)

            return self.converter.serialization(comment)[0]
