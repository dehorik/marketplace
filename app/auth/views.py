from typing import Annotated
from fastapi import APIRouter, Depends

from auth.dependencies import Login, Refresh
from auth.models import AuthorizationModel, AccessTokenModel


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/login", response_model=AuthorizationModel)
def login(auth_model: Annotated[AuthorizationModel, Depends(Login())]):
    return auth_model

@router.post("/refresh", response_model=AccessTokenModel)
def refresh(access_token: Annotated[AccessTokenModel, Depends(Refresh())]):
    return access_token
