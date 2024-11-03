from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.dependencies import (
    cart_item_creation_service,
    cart_item_load_service,
    cart_item_removal_service,
    order_creation_service,
    order_load_service,
    order_update_service,
    order_deletion_service
)
from entities.orders.models import (
    CartItemModel,
    CartItemCardListModel,
    OrderModel,
    OrderCardListModel
)


router = APIRouter(prefix='/orders', tags=['orders'])


@router.post(
    "/cart",
    response_model=CartItemModel,
    status_code=status.HTTP_201_CREATED
)
def create_cart_item(
        cart_item: Annotated[CartItemModel, Depends(cart_item_creation_service)]
):
    return cart_item

@router.get("/cart", response_model=CartItemCardListModel)
def get_cart_items(
        cart_items: Annotated[CartItemCardListModel, Depends(cart_item_load_service)]
):
    return cart_items

@router.delete("/cart/{cart_item_id}", response_model=CartItemModel)
def delete_cart_item(
        cart_item: Annotated[CartItemModel, Depends(cart_item_removal_service)]
):
    return cart_item

@router.post(
    "/",
    response_model=OrderModel,
    status_code=status.HTTP_201_CREATED
)
def create_order(
        order: Annotated[OrderModel, Depends(order_creation_service)]
):
    return order

@router.get("/latest", response_model=OrderCardListModel)
def load_orders(
        orders: Annotated[OrderCardListModel, Depends(order_load_service)]
):
    return orders

@router.patch("/{order_id}", response_model=OrderModel)
def update_order(order: Annotated[OrderModel, Depends(order_update_service)]):
    return order

@router.delete("/{order_id}", response_model=OrderModel)
def delete_order(order: Annotated[OrderModel, Depends(order_deletion_service)]):
    return order
