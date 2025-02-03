from os.path import join
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from entities.users.dependencies import (
    fetch_user_service,
    user_update_service,
    email_verification_service,
    role_management_service,
    user_deletion_service,
    fetch_users_service
)
from entities.users.models import UserModel, UserItemListModel
from core.settings import ROOT_PATH


router = APIRouter(prefix='/users', tags=['users'])

templates = Jinja2Templates(directory=join(ROOT_PATH, "frontend", "templates"))


@router.get("/me/home", response_class=HTMLResponse)
def get_user_page(request: Request):
    return templates.TemplateResponse(
        name='user.html',
        request=request
    )

@router.get("/me", response_model=UserModel)
def get_user(user: Annotated[UserModel, Depends(fetch_user_service)]):
    return user

@router.patch("/me", response_model=UserModel)
def update_user(user: Annotated[UserModel, Depends(user_update_service)]):
    return user

@router.get("/email-verification", response_class=HTMLResponse)
def get_email_verification_page(
        request: Request, token: Annotated[str, Query()]
):
    return templates.TemplateResponse(
        name='email-verification-page.html',
        request=request
    )

@router.patch("/email-verification", response_model=UserModel)
def verify_email(
        user: Annotated[UserModel, Depends(email_verification_service)]
):
    return user

@router.patch("/role", response_model=UserModel)
def set_role(user: Annotated[UserModel, Depends(role_management_service)]):
    return user

@router.delete("/me", response_model=UserModel)
def delete_user(user: Annotated[UserModel, Depends(user_deletion_service)]):
    return user

@router.get("", response_model=UserItemListModel)
def get_users(
        users: Annotated[UserItemListModel, Depends(fetch_users_service)]
):
    return users
