import os
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Path, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from entities.comments.dependencies import (
    comment_creation_service,
    comment_load_service,
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
        comment: Annotated[CommentModel, Depends(comment_deletion_service)]
):
    return comment

@router.get("/creation-form", response_class=HTMLResponse)
def get_creation_form(
        request: Request, product_id: Annotated[int, Query(ge=1)]
):
    return templates.TemplateResponse(
        name='comment_form.html',
        request=request,
        context={
            "template_type": "creation"
        }
    )

@router.get("/{comment_id}/update-form", response_class=HTMLResponse)
def get_update_form(
        request: Request, comment_id: Annotated[int, Path(ge=1)]
):
    return templates.TemplateResponse(
        name='comment_form.html',
        request=request,
        context={
            "template_type": "editing"
        }
    )
