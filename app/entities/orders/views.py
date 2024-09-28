from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.models import ShoppingBagItemModel
from entities.orders.dependencies import (
    add_to_bag_dependency,
    delete_from_bag_dependency
)


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post(
    "/shopping-bag",
    response_model=ShoppingBagItemModel,
    status_code=status.HTTP_201_CREATED
)
def add_to_bag(
        item: Annotated[ShoppingBagItemModel, Depends(add_to_bag_dependency)]
):
    return item

@router.delete("/shopping-bag", response_model=ShoppingBagItemModel)
def delete_from_bag(
        item: Annotated[ShoppingBagItemModel, Depends(delete_from_bag_dependency)]
):
    return item
