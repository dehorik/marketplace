from typing import Annotated
from fastapi import APIRouter, Depends, Cookie

from auth.dependencies import Login
from auth.models import AuthorizationModel, AccessTokenModel


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/login", response_model=AuthorizationModel)
def login(auth_model: Annotated[AuthorizationModel, Depends(Login())]):
    return auth_model

@router.post("/refresh")
def refresh(refresh_token: Annotated[str | None, Cookie()] = None):
    return {
        "refresh_token": refresh_token
    }
