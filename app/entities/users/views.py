import os
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from entities.users.dependencies import (
    user_fetch_service,
    user_update_service,
    email_verification_service,
    role_management_service,
    user_removal_service,
    fetch_admins_service
)
from entities.users.models import UserModel, AdminListModel
from core.settings import ROOT_PATH


router = APIRouter(prefix='/users', tags=['users'])


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r"frontend\templates")
)


@router.get("/me/home", response_class=HTMLResponse)
def get_user_page():
    pass

@router.get("/me", response_model=UserModel)
def get_user(user: Annotated[UserModel, Depends(user_fetch_service)]):
    return user

@router.patch("/me", response_model=UserModel)
def update_user(user: Annotated[UserModel, Depends(user_update_service)]):
    return user

@router.get("/email-verification", response_class=HTMLResponse)
def get_email_verification_page(
        request: Request, token: Annotated[str, Query()]
):
    return templates.TemplateResponse(
        name='email_verification.html',
        request=request
    )

@router.patch("/email-verification", response_model=UserModel)
def verify_email(
        user: Annotated[UserModel, Depends(email_verification_service)]
):
    return user

@router.patch("/role", response_model=UserModel)
def manage_role(user: Annotated[UserModel, Depends(role_management_service)]):
    return user

@router.delete("/me", response_model=UserModel)
def delete_user(user: Annotated[UserModel, Depends(user_removal_service)]):
    return user

@router.get("/admins", response_model=AdminListModel)
def get_admins(
        admins: Annotated[AdminListModel, Depends(fetch_admins_service)]
):
    return admins
