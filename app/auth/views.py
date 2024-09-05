from typing import Annotated
from fastapi import APIRouter, Depends

from auth.dependencies import (
    Register,
    Login,
    Logout,
    Refresh,
    AccessTokenValidator
)
from auth.models import (
    AuthorizationModel,
    AccessTokenModel,
    FullPayloadTokenModel,
    LogoutModel
)


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/register", response_model=AuthorizationModel)
def register(auth_model: Annotated[AuthorizationModel, Depends(Register())]):
    return auth_model

@router.post("/login", response_model=AuthorizationModel)
def login(auth_model: Annotated[AuthorizationModel, Depends(Login())]):
    return auth_model

@router.post("/logout", response_model=LogoutModel)
def logout(logout_model: Annotated[LogoutModel, Depends(Logout())]):
    return logout_model

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(access_token: Annotated[AccessTokenModel, Depends(Refresh())]):
    return access_token

@router.post('/validate-access', response_model=FullPayloadTokenModel)
def access(payload: Annotated[FullPayloadTokenModel, Depends(AccessTokenValidator())]):
    return payload
