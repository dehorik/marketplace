from typing import Annotated
from fastapi import APIRouter, Depends

from auth import SuccessfulAuthModel
from entities.users.dependencies import Register, Login


router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('/register', response_model=SuccessfulAuthModel)
def register(response: Annotated[SuccessfulAuthModel, Depends(Register())]):
    return response

@router.post('/login', response_model=SuccessfulAuthModel)
def login(response: Annotated[SuccessfulAuthModel, Depends(Login())]):
    return response
