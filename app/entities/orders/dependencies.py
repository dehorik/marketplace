from typing import Type, Annotated
from fastapi import HTTPException, Depends, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.orders.models import (
    ShoppingBagItemModel,
    ShoppingBagItemCardModel,
    ShoppingBagItemCardListModel
)
from auth import Authorization, PayloadTokenModel
from core.database import OrderDataBase
from utils import Converter


base_user_dependency = Authorization(min_role_id=1)


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            order_database: Type = OrderDataBase
    ):
        self.order_database = order_database


class ShoppingBagItemSaver(BaseDependency):
    """Добавление товара в корзину"""

    def __init__(self, converter: Converter = Converter(ShoppingBagItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            product_id: int
    ) -> ShoppingBagItemModel:
        try:
            with self.order_database() as order_db:
                shopping_bag_item = order_db.add_to_shopping_bag(
                    user_id=payload.sub,
                    product_id=product_id
                )

            return self.converter.serialization(shopping_bag_item)[0]
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


class ShoppingBagItemDeleter(BaseDependency):
    """Удаление товара из корзины"""

    def __init__(self, converter: Converter = Converter(ShoppingBagItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            item_id: int
    ) -> ShoppingBagItemModel:
        with self.order_database() as order_db:
            shopping_bag_item = order_db.delete_from_shopping_bag(
                user_id=payload.sub,
                shopping_bag_item_id=item_id
            )

        if not shopping_bag_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect item_id"
            )

        return self.converter.serialization(shopping_bag_item)[0]


class ShoppingBagItemLoader(BaseDependency):
    """Загрузка карточек товаров в корзине"""

    def __init__(
            self,
            converter: Converter = Converter(ShoppingBagItemCardModel)
    ):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_item_id: Annotated[int | None, Query(ge=1)] = None
    ) -> ShoppingBagItemCardListModel:
        """
        :param amount: требуемое количество карточек
        :param last_item_id: id карточки из последней подгрузки;
                             если это первый запрос на получение карточек,
                             оставить None

        :return: список из карточек товаров
        """

        try:
            with self.order_database() as order_db:
                shopping_bag_items = order_db.get_shopping_bag_items(
                    user_id=payload.sub,
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
