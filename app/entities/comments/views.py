import os
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.templating import Jinja2Templates

from entities.comments.dependencies import (
    comment_creation_service,
    fetch_comments_service,
    comment_update_service,
    comment_deletion_service
)
from entities.comments.models import CommentModel, CommentItemListModel
from core.settings import ROOT_PATH


router = APIRouter(prefix='/comments', tags=['comments'])


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r"frontend\templates")
)


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
def get_comments(
        comments: Annotated[CommentItemListModel, Depends(fetch_comments_service)]
):
    return comments

@router.patch("/{comment_id}", response_model=CommentModel)
def update_comment(
        comment: Annotated[CommentModel, Depends(comment_update_service)]
):
    return comment

@router.delete('/{comment_id}', response_model=CommentModel)
def delete_comment(
        comment: Annotated[CommentModel, Depends(comment_deletion_service)]
):
    return comment
