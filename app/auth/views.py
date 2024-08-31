from typing import Annotated
from fastapi import APIRouter, Depends

from auth.models import SuccessfulAuthModel


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


# @router.post('/register', response_model=SuccessfulAuthModel)
# def register(response: Annotated[SuccessfulAuthModel, Depends(Register())]):
#     return response
#
# @router.post('/login', response_model=SuccessfulAuthModel)
# def login(response: Annotated[SuccessfulAuthModel, Depends(Login())]):
#     return response
