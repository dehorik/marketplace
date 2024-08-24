from typing import Annotated
from fastapi import APIRouter, Form, UploadFile, status

from core.database import Session, CommentDataBase
from core.models import CommentModel
from utils import FileWriter, FileReWriter, FileDeleter, Converter


router = APIRouter(
    prefix='/comments',
    tags=['comments']
)


@router.post(
    '/create',
    response_model=CommentModel,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
        user_id: int,
        product_id: int,
        comment_rating: Annotated[int, Form(ge=1, le=5)],
        comment_text: Annotated[str | None, Form(min_length=3, max_length=200)] = None,
        comment_photo: UploadFile | None = None
):
    converter = Converter(CommentModel)
    session = Session()
    db = CommentDataBase(session)

    comment_photo_path = None
    if comment_photo:
        writer = FileWriter()
        comment_photo_path = writer(FileWriter.comment_path, comment_photo.file.read())

    comment = db.create(
        user_id,
        product_id,
        comment_text,
        comment_rating,
        comment_photo_path
    )
    model = converter.serialization(comment)[0]

    db.close()
    return model

@router.put('/{comment_id}', response_model=CommentModel)
def update_comment(
        comment_id: int,
        comment_text: str,
        comment_rating: int,
        comment_photo_path: str | None = None,
        comment_photo: UploadFile | None = None
):
    session = Session()
    db = CommentDataBase(session)
    converter = Converter(CommentModel)

    if comment_photo:
        file_writer = FileWriter()
        comment_photo_path = file_writer(FileWriter.comment_path, comment_photo.file.read())

    elif comment_photo_path and comment_photo:
        file_rewriter = FileReWriter()
        file_rewriter(comment_photo_path, comment_photo.file.read())

    comment = db.update(
        comment_id,
        comment_text,
        comment_rating,
        comment_photo_path
    )
    model = converter.serialization(comment)[0]

    db.close()
    return model

@router.delete('/{comment_id}', response_model=CommentModel)
def delete_comment(comment_id: int):
    file_deleter = FileDeleter()
    session = Session()
    db = CommentDataBase(session)

    comment = db.delete(comment_id)[0]
    deleted_comment_path = comment[-1]
    file_deleter(deleted_comment_path)

    db.close()
    return comment
