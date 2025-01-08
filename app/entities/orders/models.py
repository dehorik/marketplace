from typing import List
from datetime import date
from pydantic import BaseModel, Field


class OrderCreationRequest(BaseModel):
    product_id: int = Field(ge=1)
    delivery_address: str = Field(min_length=6, max_length=30)


class OrderUpdateRequest(BaseModel):
    delivery_address: str = Field(min_length=6, max_length=30)


class OrderModel(BaseModel):
    """Базовая схема заказа"""

    order_id: int
    user_id: int
    product_id: int
    product_name: str
    product_price: int
    date_start: date
    date_end: date
    delivery_address: str
    photo_path: str


class OrderCardModel(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    product_name: str
    product_price: int
    date_start: date
    date_end: date
    delivery_address: str
    photo_path: str


class OrderCardListModel(BaseModel):
    orders: List[OrderCardModel]
