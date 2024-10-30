from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.comments.dependencies import (
    comment_creation_service,
    comment_load_service,
    comment_update_service,
    comment_removal_service
)
from entities.comments.models import CommentModel, CommentItemListModel


router = APIRouter(prefix='/comments', tags=['comments'])


@router.post(
    "/",
    response_model=CommentModel,
    status_code=status.HTTP_201_CREATED
)
def create_comment(
        comment: Annotated[CommentModel, Depends(comment_creation_service)]
):
    return comment

@router.get("/latest", response_model=CommentItemListModel)
def load_comments(
        comments: Annotated[CommentItemListModel, Depends(comment_load_service)]
):
    return comments

@router.patch("/{comment_id}", response_model=CommentModel)
def update_comment(
        comment: Annotated[CommentModel, Depends(comment_update_service)]
):
    return comment

@router.delete('/{comment_id}', response_model=CommentModel)
def delete_comment(
        comment: Annotated[CommentModel, Depends(comment_removal_service)]
):
    return comment
