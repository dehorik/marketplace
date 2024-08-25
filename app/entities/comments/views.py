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
def create_comment(obj: Annotated[CreateComment, Depends(CreateComment)]):
    return obj.comment

@router.patch('/{comment_id}', response_model=CommentModel)
def update_comment(obj: Annotated[UpdateComment, Depends(UpdateComment)]):
    return obj.comment

@router.delete('/{comment_id}', response_model=CommentModel)
def delete_comment(obj: Annotated[DeleteComment, Depends(DeleteComment)]):
    return obj.comment
