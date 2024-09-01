from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.comments.models import CommentModel
from entities.comments.dependencies import CreateComment, UpdateComment, DeleteComment


router = APIRouter(
    prefix='/comments',
    tags=['comments']
)


@router.post(
    '/create',
    response_model=CommentModel,
    status_code=status.HTTP_201_CREATED
)
def create_comment(comment: Annotated[CommentModel, Depends(CreateComment())]):
    return comment

@router.patch('/{comment_id}', response_model=CommentModel)
def update_comment(comment: Annotated[CommentModel, Depends(UpdateComment())]):
    return comment

@router.delete('/{comment_id}', response_model=CommentModel)
def delete_comment(comment: Annotated[CommentModel, Depends(DeleteComment())]):
    return comment
