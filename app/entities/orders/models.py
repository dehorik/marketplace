from typing import List
from pydantic import BaseModel


class ShoppingBagItemModel(BaseModel):
    shopping_bag_item_id: int
    product_id: int
    user_id: int


class ShoppingBagItemCardModel(BaseModel):
    shopping_bag_item_id: int
    user_id: int
    product_id: int
    product_name: str
    product_price: int


class ShoppingBagItemCardListModel(BaseModel):
    shopping_bag_items: List[ShoppingBagItemCardModel]
