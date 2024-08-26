from typing import Annotated

from fastapi import APIRouter, status, Depends

from auth.dependencies import Register
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
