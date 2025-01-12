import os
from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from entities.cart_items.dependencies import (
    cart_item_creation_service,
    fetch_cart_items_service,
    cart_item_deletion_service
)
from entities.cart_items.models import CartItemModel, CartItemCardListModel
from core.settings import ROOT_PATH


router = APIRouter(prefix='/cart-items', tags=['cart-items'])


templates = Jinja2Templates(
    directory=os.path.join(ROOT_PATH, r"frontend\templates")
)


@router.post("", response_model=CartItemModel, status_code=status.HTTP_201_CREATED)
def create_cart_item(
        cart_item: Annotated[CartItemModel, Depends(cart_item_creation_service)]
):
    return cart_item

@router.get("", response_class=HTMLResponse)
def get_cart_items_page(request: Request):
    return templates.TemplateResponse(
        name='cart.html',
        request=request,
    )

@router.get("/latest", response_model=CartItemCardListModel)
def get_cart_items(
        cart_items: Annotated[CartItemCardListModel, Depends(fetch_cart_items_service)]
):
    return cart_items

@router.delete("/{cart_item_id}", response_model=CartItemModel)
def delete_cart_item(
        cart_item: Annotated[CartItemModel, Depends(cart_item_deletion_service)]
):
    return cart_item
