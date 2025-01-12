from typing import List
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
    product_name: str
    product_price: int
    product_photo_path: str


class CartItemCardListModel(BaseModel):
    cart_items: List[CartItemCardModel]
