from typing import List
from datetime import datetime
from pydantic import BaseModel, Field


class CartItemCreationRequest(BaseModel):
    product_id: int = Field(ge=1)


class CartItemModel(BaseModel):
    """Базовая схема элемента корзины"""

    cart_item_id: int
    user_id: int
    product_id: int


class CartItemCardModel(BaseModel):
    """Схема товара в корзине для подгрузки на страницу"""

    cart_item_id: int
    user_id: int
    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)


class CartItemCardListModel(BaseModel):
    cart_items: List[CartItemCardModel]


class OrderCreationRequest(BaseModel):
    product_id: int = Field(ge=1)
    delivery_address: str = Field(min_length=6, max_length=30)


class OrderModel(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    product_name: str
    product_price: int
    date_start: datetime
    date_end: datetime
    delivery_address: str
    photo_path: str
