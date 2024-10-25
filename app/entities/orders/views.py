from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.dependencies import (
    cart_item_creation_service,
    cart_item_removal_service,
    cart_item_loader_service,
    order_creation_service
)
from entities.orders.models import (
    CartItemModel,
    CartItemCardListModel,
    OrderModel
)


router = APIRouter(prefix='/orders', tags=['orders'])


@router.post(
    "/cart",
    response_model=CartItemModel,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
        cart_item: Annotated[CartItemModel, Depends(cart_item_creation_service)]
):
    return cart_item

@router.delete("/cart/{item_id}", response_model=CartItemModel)
def delete_from_cart(
        cart_item: Annotated[CartItemModel, Depends(cart_item_removal_service)]
):
    return cart_item

@router.get("/cart", response_model=CartItemCardListModel)
def get_cart(
        cart_items: Annotated[CartItemCardListModel, Depends(cart_item_loader_service)]
):
    return cart_items

@router.post(
    "/",
    response_model=OrderModel,
    status_code=status.HTTP_201_CREATED
)
def create_order(
        order: Annotated[OrderModel, Depends(order_creation_service)]
):
    return order
