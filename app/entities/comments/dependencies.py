from typing import Annotated
from fastapi import Form, UploadFile, HTTPException, status
from psycopg2.errors import ForeignKeyViolation

from core.database import Session, CommentDataBase
from entities.comments.models import CommentModel
from utils import FileWriter, FileReWriter, FileDeleter, Converter


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
                    detail='incorrect comment_photo file type!'
                )

        converter = Converter(CommentModel)
        session = Session()
        comment_db = CommentDataBase(session)

        if comment_photo:
            file_writer = FileWriter()
            comment_photo_path = file_writer(FileWriter.comment_path, comment_photo.file.read())
        else:
            comment_photo_path = None

        try:
            comment = comment_db.create(
                user_id,
                product_id,
                comment_rating,
                comment_text,
                comment_photo_path
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect user_id or product_id'
            )
        else:
            self.comment = converter.serialization(comment)[0]
        finally:
            comment_db.close()


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
                    detail='incorrect comment_photo file type!'
                )

        session = Session()
        comment_db = CommentDataBase(session)
        converter = Converter(CommentModel)

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
                file_rewriter = FileReWriter()
                file_rewriter(comment[0][-1], comment_photo.file.read())
            else:
                file_writer = FileWriter()
                comment_photo_path = file_writer(FileWriter.comment_path, comment_photo.file.read())
                comment = comment_db.update(comment_id, comment_photo_path=comment_photo_path)

        comment_db.close()
        self.comment = converter.serialization(comment)[0]


class DeleteComment:
    def __init__(self, comment_id: int):
        converter = Converter(CommentModel)
        session = Session()
        comment_db = CommentDataBase(session)

        comment = comment_db.delete(comment_id)
        if not comment:
            comment_db.close()

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect comment_id'
            )

        if comment[0][-1]:
            file_deleter = FileDeleter()
            file_deleter(comment[0][-1])

        comment_db.close()
        self.comment = converter.serialization(comment)[0]
