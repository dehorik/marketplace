import os
from typing import Annotated
from fastapi import APIRouter, Depends, Request, Query, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from auth.dependencies import (
    registration_service,
    login_service,
    logout_service,
    token_refresh_service,
)
from auth.models import ExtendedUserModel, AccessTokenModel
from core.settings import ROOT_PATH


router = APIRouter(prefix='/auth', tags=['auth'])


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r"frontend\templates")
)


@router.post(
    "/registration",
    response_model=ExtendedUserModel,
    status_code=status.HTTP_201_CREATED
)
def registration(
        user: Annotated[ExtendedUserModel, Depends(registration_service)]
):
    return user

@router.post("/login", response_model=ExtendedUserModel)
def login(
        user: Annotated[ExtendedUserModel, Depends(login_service)]
):
    return user

@router.post("/logout")
def logout(response: Annotated[dict, Depends(logout_service)]):
    return response

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(
        access_token: Annotated[AccessTokenModel, Depends(token_refresh_service)]
):
    return access_token

@router.get("/form", response_class=HTMLResponse)
def get_auth_form(request: Request, redirect_url: Annotated[str, Query()]):
    return templates.TemplateResponse(
        name="auth-form.html",
        request=request
    )
