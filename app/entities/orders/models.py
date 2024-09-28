from pydantic import BaseModel


class ShoppingBagItemModel(BaseModel):
    shopping_bag_item_id: int
    product_id: int
    user_id: int
