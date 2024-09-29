from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.models import (
    ShoppingBagItemModel,
    ShoppingBagItemCardListModel
)
from entities.orders.dependencies import (
    add_to_shopping_bag_dependency,
    delete_from_shopping_bag_dependency,
    get_shopping_bag_dependency
)


router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@router.post("/shopping-bag", status_code=status.HTTP_201_CREATED)
def add_to_shopping_bag(
        shopping_bag_item: Annotated[
            ShoppingBagItemModel,
            Depends(add_to_shopping_bag_dependency)
        ]
) -> ShoppingBagItemModel:
    return shopping_bag_item

@router.delete("/shopping-bag")
def delete_from_shopping_bag(
        shopping_bag_item: Annotated[
            ShoppingBagItemModel,
            Depends(delete_from_shopping_bag_dependency)
        ]
) -> ShoppingBagItemModel:
    return shopping_bag_item

@router.get("/shopping-bag")
def get_shopping_bag(
        shopping_bag_items: Annotated[
            ShoppingBagItemCardListModel,
            Depends(get_shopping_bag_dependency)
        ]
) -> ShoppingBagItemCardListModel:
    return shopping_bag_items
