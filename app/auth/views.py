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


# dependencies
register_user = Register()
login_user = Login()
logout_user = Logout()
refresh_tokens = Refresh()
validate_access_token = AccessTokenValidator()


@router.post("/register", response_model=AuthorizationModel)
def register(auth_model: Annotated[AuthorizationModel, Depends(register_user)]):
    return auth_model

@router.post("/login", response_model=AuthorizationModel)
def login(auth_model: Annotated[AuthorizationModel, Depends(login_user)]):
    return auth_model

@router.post("/logout", response_model=LogoutModel)
def logout(logout_model: Annotated[LogoutModel, Depends(logout_user)]):
    return logout_model

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(access_token: Annotated[AccessTokenModel, Depends(refresh_tokens)]):
    return access_token

@router.post('/validate-access', response_model=FullPayloadTokenModel)
def access(payload: Annotated[FullPayloadTokenModel, Depends(validate_access_token)]):
    return payload
