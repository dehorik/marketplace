from typing import Annotated
from fastapi import Form, UploadFile, HTTPException, status

from core.config_reader import config
from core.database import CommentDataBase
from utils import FileWriter, FileReWriter, FileDeleter, Converter
from entities.comments.models import CommentModel


class CreateComment:
    def __init__(
            self,
            user_id: int,
            product_id: int,
            comment_rating: Annotated[int, Form(ge=1, le=5)],
            comment_text: Annotated[str | None, Form(min_length=3, max_length=200)] = None,
            comment_photo: UploadFile | None = None
    ):
        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        converter = Converter(CommentModel)

        if comment_photo:
            comment_photo_path = FileWriter(
                config.getenv("COMMENT_PHOTO_PATH"),
                comment_photo.file.read()
            ).path
        else:
            comment_photo_path = None

        with CommentDataBase() as comment_db:
            comment = comment_db.create(
                user_id,
                product_id,
                comment_rating,
                comment_text,
                comment_photo_path
            )
            self.comment = converter.serialization(comment)[0]


class UpdateComment:
    def __init__(
            self,
            comment_id: int,
            comment_text: Annotated[str | None, Form(min_length=3, max_length=200)] = None,
            comment_rating: Annotated[int | None, Form(ge=1, le=5)] = None,
            comment_photo: UploadFile | None = None
    ):
        if comment_photo:
            if not comment_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )
        converter = Converter(CommentModel)

        with CommentDataBase() as comment_db:
            params = {
                "comment_text": comment_text,
                "comment_rating": comment_rating
            }
            params = {key: value for key, value in params.items() if value is not None}
            comment = comment_db.update(comment_id, **params)

            if not comment:
                comment_db.close()

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='incorrect comment_id'
                )

            if comment_photo:
                if comment[0][-1]:
                    FileReWriter(comment[0][-1], comment_photo.file.read())
                else:
                    comment_photo_path = FileWriter(
                        config.getenv("COMMENT_PHOTO_PATH"),
                        comment_photo.file.read()
                    ).path
                    comment = comment_db.update(comment_id, comment_photo_path=comment_photo_path)

            self.comment = converter.serialization(comment)[0]


class DeleteComment:
    def __init__(self, comment_id: int):
        converter = Converter(CommentModel)

        with CommentDataBase() as comment_db:
            comment = comment_db.delete(comment_id)

            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='incorrect comment_id'
                )

            deleted_comment_photo_path = comment[0][-1]
            if deleted_comment_photo_path:
                FileDeleter(deleted_comment_photo_path)

            self.comment = converter.serialization(comment)[0]