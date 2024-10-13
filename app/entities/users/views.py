import os
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from entities.users.dependencies import (
    user_data_getting_service,
    user_data_update_service,
    email_verification_service,
    role_update_service
)
from entities.users.models import UserModel
from core.settings import ROOT_PATH


router = APIRouter(
    prefix='/users',
    tags=['users']
)


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r"frontend\templates")
)


@router.get("/me", response_class=HTMLResponse)
def get_user_page():
    pass

@router.get("/me/data", response_model=UserModel)
def get_user_data(
        user: Annotated[UserModel, Depends(user_data_getting_service)]
):
    return user

@router.patch("/me/data", response_model=UserModel)
def update_user_data(
        user: Annotated[UserModel, Depends(user_data_update_service)]
):
    return user

@router.get("/email-verification", response_class=HTMLResponse)
def get_email_verification_page(
        request: Request,
        token: Annotated[str, Query()]
):
    return templates.TemplateResponse(
        name='email_verification.html',
        request=request
    )

@router.patch("/email-verification")
def verify_email(
        response: Annotated[dict, Depends(email_verification_service)]
):
    return response

@router.patch("/role", response_model=UserModel)
def update_role(user: Annotated[UserModel, Depends(role_update_service)]):
    return user
