from typing import Annotated
from fastapi import APIRouter, Form, UploadFile, status

from core.database import Session, CommentDataBase
from core.models import CommentModel
from utils import Converter, FileWriter


comment_router = APIRouter(
    prefix='/comments',
    tags=['comments']
)


@comment_router.post(
    '/create',
    response_model=CommentModel,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
        user_id: int,
        product_id: int,
        comment_text: Annotated[str, Form(min_length=3, max_length=200)],
        comment_rating: Annotated[int, Form(ge=1, le=5)],
        comment_photo: UploadFile | None = None
):
    converter = Converter(CommentModel)
    session = Session()
    db = CommentDataBase(session)

    comment_photo_path = None
    if comment_photo:
        writer = FileWriter(FileWriter.comment)
        comment_photo_path = writer(comment_photo.file.read())

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

@comment_router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int):
    session = Session()
    db = CommentDataBase(session)

    db.delete(comment_id)
    db.close()
