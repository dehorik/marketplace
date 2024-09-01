from typing import Annotated
from fastapi import APIRouter, Depends

from auth.dependencies import Login
from auth.models import AuthorizationModel


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post("/login", response_model=AuthorizationModel)
def login(auth_model: Annotated[AuthorizationModel, Depends(Login())]):
    return auth_model
