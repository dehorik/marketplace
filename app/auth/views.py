from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from auth.dependencies import (
    register_user_dependency,
    login_user_dependency,
    logout_user_dependency,
    refresh_tokens_dependency,
    validate_access_token_dependency
)
from auth.models import (
    AuthenticationModel,
    AccessTokenModel,
    PayloadTokenModel
)


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


templates = Jinja2Templates(
    directory='../frontend/templates'
)


@router.post("/registration", response_model=AuthenticationModel)
def register(
        auth_model: Annotated[AuthenticationModel, Depends(register_user_dependency)]
):
    return auth_model

@router.post("/login", response_model=AuthenticationModel)
def login(
        auth_model: Annotated[AuthenticationModel, Depends(login_user_dependency)]
):
    return auth_model

@router.post("/logout")
def logout(response: Annotated[str, Depends(logout_user_dependency)]):
    return {
        "message": response
    }

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(
        access_token: Annotated[AccessTokenModel, Depends(refresh_tokens_dependency)]
):
    return access_token

@router.get('/access-token-validator', response_model=PayloadTokenModel)
def access(
        payload: Annotated[PayloadTokenModel, Depends(validate_access_token_dependency)]
):
    return payload

@router.get("/registration-page", response_class=HTMLResponse)
def get_registration_page(request: Request):
    return templates.TemplateResponse(
        name='registration.html',
        request=request
    )
