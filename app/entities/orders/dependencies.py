from typing import Type
from fastapi import HTTPException, status

from entities.orders.models import ShoppingBagItemModel
from core.database import OrderDataBase
from utils import Converter


class BaseDependency:
    def __init__(
            self,
            order_database: Type = OrderDataBase
    ):
        self.order_database = order_database


class ShoppingBagSaver(BaseDependency):
    def __init__(self, converter: Converter = Converter(ShoppingBagItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, user_id: int, product_id: int) -> ShoppingBagItemModel:
        with self.order_database() as order_db:
            shopping_bag_item = order_db.add_to_shopping_bag(
                product_id=product_id,
                user_id=user_id
            )

        return self.converter.serialization(shopping_bag_item)[0]


class ShoppingBagDeleter(BaseDependency):
    def __init__(self, converter: Converter = Converter(ShoppingBagItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, item_id: int) -> ShoppingBagItemModel:
        with self.order_database() as order_db:
            shopping_bag_item = order_db.delete_from_shopping_bag(item_id)

        if not shopping_bag_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect item_id"
            )

        return self.converter.serialization(shopping_bag_item)[0]


# dependencies
add_to_bag_dependency = ShoppingBagSaver()
delete_from_bag_dependency = ShoppingBagDeleter()
