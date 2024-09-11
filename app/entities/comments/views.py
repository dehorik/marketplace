from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.comments.dependencies import (
    create_comment_dependency,
    load_comments_dependency,
    update_comment_dependency,
    delete_comment_dependency
)
from entities.comments.models import CommentModel, CommentItemListModel


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
        comment: Annotated[CommentModel, Depends(create_comment_dependency)]
):
    return comment

@router.get("/latest", response_model=CommentItemListModel)
def load_comment_list(
        comments: Annotated[CommentItemListModel, Depends(load_comments_dependency)]
):
    return comments

@router.patch('/{comment_id}', response_model=CommentModel)
def update_comment(
        comment: Annotated[CommentModel, Depends(update_comment_dependency)]
):
    return comment

@router.delete('/{comment_id}', response_model=CommentModel)
def delete_comment(
        comment: Annotated[CommentModel, Depends(delete_comment_dependency)]
):
    return comment
