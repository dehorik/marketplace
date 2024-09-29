from typing import Type
from fastapi import HTTPException, status
from psycopg2.errors import ForeignKeyViolation

from entities.orders.models import (
    ShoppingBagItemModel,
    ShoppingBagItemCardModel,
    ShoppingBagItemCardListModel
)
from core.database import OrderDataBase
from utils import Converter


class BaseDependency:
    def __init__(
            self,
            order_database: Type = OrderDataBase
    ):
        self.order_database = order_database


class ShoppingBagItemSaver(BaseDependency):
    def __init__(self, converter: Converter = Converter(ShoppingBagItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, user_id: int, product_id: int) -> ShoppingBagItemModel:
        try:
            with self.order_database() as order_db:
                shopping_bag_item = order_db.add_to_shopping_bag(
                    product_id=product_id,
                    user_id=user_id
                )

            return self.converter.serialization(shopping_bag_item)[0]
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


class ShoppingBagItemDeleter(BaseDependency):
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


class ShoppingBagItemLoader(BaseDependency):
    def __init__(self, converter: Converter = Converter(ShoppingBagItemCardModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            user_id: int,
            amount: int = 10,
            last_item_id: int | None = None
    ) -> ShoppingBagItemCardListModel:
        try:
            with self.order_database() as order_db:
                shopping_bag_items = order_db.get_shopping_bag_items(
                    user_id=user_id,
                    amount=amount,
                    last_item_id=last_item_id
                )

            return ShoppingBagItemCardListModel(
                shopping_bag_items=self.converter.serialization(shopping_bag_items)
            )

        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


# dependencies
add_to_shopping_bag_dependency = ShoppingBagItemSaver()
delete_from_shopping_bag_dependency = ShoppingBagItemDeleter()
get_shopping_bag_dependency = ShoppingBagItemLoader()
