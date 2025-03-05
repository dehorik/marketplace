from typing import List
from pydantic import BaseModel, Field


class CartItemCreationRequest(BaseModel):
    """Схема данных в теле запроса на добавление товара в корзину"""

    product_id: int = Field(ge=1)


class CartItemModel(BaseModel):
    """Базовая схема товара в корзине"""

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


class CartItemCardListModel(BaseModel):
    """Схема списка из товаров в корзине для подгрузки на страницу"""

    cart_items: List[CartItemCardModel]
