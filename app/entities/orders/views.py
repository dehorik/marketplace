from typing import Annotated
from fastapi import APIRouter, Depends, status

from entities.orders.dependencies import (
    order_creation_service,
    fetch_orders_service,
    order_update_service,
    order_deletion_service
)
from entities.orders.models import OrderModel, OrderCardListModel


router = APIRouter(prefix='/orders', tags=['orders'])


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
def get_orders(
        orders: Annotated[OrderCardListModel, Depends(fetch_orders_service)]
):
    return orders

@router.patch("/{order_id}", response_model=OrderModel)
def update_order(order: Annotated[OrderModel, Depends(order_update_service)]):
    return order

@router.delete("/{order_id}", response_model=OrderModel)
def delete_order(order: Annotated[OrderModel, Depends(order_deletion_service)]):
    return order
