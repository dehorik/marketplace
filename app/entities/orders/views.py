from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.dependencies import (
    add_to_cart_dependency,
    delete_from_cart_dependency,
    get_cart_dependency
)
from entities.orders.models import CartItemModel, CartItemCardListModel


orders_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

cart_router = APIRouter(
    prefix='/cart',
    tags=['cart items']
)

orders_router.include_router(cart_router)


@cart_router.post(
    "/create",
    response_model=CartItemModel,
    status_code=status.HTTP_201_CREATED
)
def add_to_cart(
        cart_item: Annotated[CartItemModel, Depends(add_to_cart_dependency)]
):
    return cart_item

@cart_router.delete("/{cart_item_id}", response_model=CartItemModel)
def delete_from_cart(
        cart_item: Annotated[CartItemModel, Depends(delete_from_cart_dependency)]
):
    return cart_item

@cart_router.get("/", response_model=CartItemCardListModel)
def get_cart(
        cart_items: Annotated[CartItemCardListModel, Depends(get_cart_dependency)]
):
    return cart_items
