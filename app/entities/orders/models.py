from typing import List
from pydantic import BaseModel, Field


class CartItemModel(BaseModel):
    """Базовая схема элемента корзины"""

    cart_item_id: int
    product_id: int
    user_id: int


class CartItemCardModel(BaseModel):
    """Схема товара в корзине для подгрузки на страницу"""

    cart_item_id: int
    user_id: int
    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)


class CartItemCardListModel(BaseModel):
    cart_items: List[CartItemCardModel]
