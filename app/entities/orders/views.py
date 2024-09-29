from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.dependencies import (
    add_to_shopping_bag_dependency,
    delete_from_shopping_bag_dependency,
    get_shopping_bag_dependency
)
from entities.orders.models import (
    ShoppingBagItemModel,
    ShoppingBagItemCardListModel
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
def add_to_shopping_bag(
        shopping_bag_item: Annotated[
            ShoppingBagItemModel,
            Depends(add_to_shopping_bag_dependency)
        ]
):
    return shopping_bag_item

@router.delete("/shopping-bag/{item_id}", response_model=ShoppingBagItemModel)
def delete_from_shopping_bag(
        shopping_bag_item: Annotated[
            ShoppingBagItemModel,
            Depends(delete_from_shopping_bag_dependency)
        ]
):
    return shopping_bag_item

@router.get("/shopping-bag", response_model=ShoppingBagItemCardListModel)
def get_shopping_bag(
        shopping_bag_items: Annotated[
            ShoppingBagItemCardListModel,
            Depends(get_shopping_bag_dependency)
        ]
):
    return shopping_bag_items
