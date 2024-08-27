from typing import Annotated
from fastapi import APIRouter, status, Depends

from auth.dependencies import Register, Login
from entities.users.models import UserModel


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post(
    '/register',
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED
)
def register(obj: Annotated[Register, Depends(Register)]):
    return obj.user

@router.post('/login', response_model=UserModel)
def login(obj: Annotated[Login, Depends(Login)]):
    return obj.user
