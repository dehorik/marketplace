from typing import Annotated
from fastapi import APIRouter, Depends

from entities.users.models import UserModel
from entities.users.dependencies import get_user_dependency


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get("/me", response_model=UserModel)
def get_user(user: Annotated[UserModel, Depends(get_user_dependency)]):
    return user
