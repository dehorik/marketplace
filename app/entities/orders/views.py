from os.path import join
from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from entities.orders.dependencies import (
    order_creation_service,
    fetch_orders_service,
    order_update_service,
    order_deletion_service
)
from entities.orders.models import OrderModel, OrderListModel
from core.settings import ROOT_PATH


router = APIRouter(prefix='/orders', tags=['orders'])

templates = Jinja2Templates(directory=join(ROOT_PATH, "frontend", "templates"))


@router.post("", response_model=OrderModel, status_code=status.HTTP_201_CREATED)
def create_order(
        order: Annotated[OrderModel, Depends(order_creation_service)]
):
    return order

@router.get("", response_class=HTMLResponse)
def get_orders_page(request: Request):
    return templates.TemplateResponse(
        name='orders.html',
        request=request,
    )

@router.get("/latest", response_model=OrderListModel)
def get_orders(
        orders: Annotated[OrderListModel, Depends(fetch_orders_service)]
):
    return orders

@router.patch("/{order_id}", response_model=OrderModel)
def update_order(order: Annotated[OrderModel, Depends(order_update_service)]):
    return order

@router.delete("/{order_id}", response_model=OrderModel)
def delete_order(order: Annotated[OrderModel, Depends(order_deletion_service)]):
    return order
