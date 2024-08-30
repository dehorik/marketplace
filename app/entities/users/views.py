from typing import Annotated
from fastapi import APIRouter, Depends

from auth import SuccessfulAuthModel
from entities.users.dependencies import Register, Login


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/register', response_model=SuccessfulAuthModel)
def register(obj: Annotated[Register, Depends(Register)]):
    return obj.successful_reg_data

@router.post('/login', response_model=SuccessfulAuthModel)
def login(obj: Annotated[Login, Depends(Login)]):
    return obj.data
