from typing import Annotated
from fastapi import APIRouter, Depends

from auth.dependencies import (
    register_user,
    login_user,
    logout_user,
    refresh_tokens,
    validate_access_token
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


@router.post("/register", response_model=AuthenticationModel)
def register(auth_model: Annotated[AuthenticationModel, Depends(register_user)]):
    return auth_model

@router.post("/login", response_model=AuthenticationModel)
def login(auth_model: Annotated[AuthenticationModel, Depends(login_user)]):
    return auth_model

@router.post("/logout")
def logout(response: Annotated[str, Depends(logout_user)]):
    return {
        "message": response
    }

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(access_token: Annotated[AccessTokenModel, Depends(refresh_tokens)]):
    return access_token

@router.get('/validate-access', response_model=PayloadTokenModel)
def access(payload: Annotated[PayloadTokenModel, Depends(validate_access_token)]):
    return payload
