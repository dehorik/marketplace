from typing import List
from pydantic import BaseModel, Field


class ShoppingBagItemModel(BaseModel):
    """Базовая модель товара в корзине"""

    shopping_bag_item_id: int
    product_id: int
    user_id: int


class ShoppingBagItemCardModel(BaseModel):
    """Модель товара в корзине для подгрузки на страницу"""

    shopping_bag_item_id: int
    user_id: int
    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)


class ShoppingBagItemCardListModel(BaseModel):
    shopping_bag_items: List[ShoppingBagItemCardModel]
