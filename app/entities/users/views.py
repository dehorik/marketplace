from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from entities.users.dependencies import (
    user_data_getting_service,
    role_update_service
)
from entities.users.models import UserModel


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get("/me", response_class=HTMLResponse)
def get_user_page():
    pass

@router.get("/me/data", response_model=UserModel)
def get_user_data(
        user: Annotated[UserModel, Depends(user_data_getting_service)]
):
    return user

@router.patch("/role", response_model=UserModel)
def update_role(user: Annotated[UserModel, Depends(role_update_service)]):
    return user
