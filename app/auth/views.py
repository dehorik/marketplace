from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from auth.dependencies import (
    registration_dependency,
    login_dependency,
    logout_dependency,
    refresh_dependency,
)
from auth.models import AuthenticationModel, AccessTokenModel


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


templates = Jinja2Templates(
    directory='../frontend/templates'
)


@router.post("/registration", response_model=AuthenticationModel)
def registration(
        auth_model: Annotated[AuthenticationModel, Depends(registration_dependency)]
):
    return auth_model

@router.post("/login", response_model=AuthenticationModel)
def login(
        auth_model: Annotated[AuthenticationModel, Depends(login_dependency)]
):
    return auth_model

@router.post("/logout")
def logout(response: Annotated[str, Depends(logout_dependency)]):
    return response

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(
        access_token: Annotated[AccessTokenModel, Depends(refresh_dependency)]
):
    return access_token

@router.get("/registration", response_class=HTMLResponse)
def get_registration_page(request: Request):
    return templates.TemplateResponse(
        name='registration.html',
        request=request
    )

@router.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse(
        name='login.html',
        request=request
    )
