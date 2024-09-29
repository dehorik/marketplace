from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from entities.users.dependencies import (
    get_user_data_dependency,
    update_role_dependency
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
        user: Annotated[UserModel, Depends(get_user_data_dependency)]
):
    return user

@router.put("/role", response_model=UserModel)
def update_role(user: Annotated[UserModel, Depends(update_role_dependency)]):
    return user
