from typing import Type, Annotated
from fastapi import HTTPException, Depends, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.orders.models import (
    CartItemModel,
    CartItemCardModel,
    CartItemCardListModel
)
from auth import Authorization, PayloadTokenModel
from core.database import OrderDataBase
from utils import Converter


base_user_dependency = Authorization(min_role_id=1)


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            order_database: Type[OrderDataBase] = OrderDataBase
    ):
        self.order_database = order_database


class CartItemSaver(BaseDependency):
    """Добавление товара в корзину"""

    def __init__(self, converter: Converter = Converter(CartItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            product_id: int
    ) -> CartItemModel:
        try:
            with self.order_database() as order_db:
                cart_item = order_db.add_to_cart(
                    user_id=payload.sub,
                    product_id=product_id
                )

            return self.converter.serialization(cart_item)[0]
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


class CartItemDeleter(BaseDependency):
    """Удаление товара из корзины"""

    def __init__(self, converter: Converter = Converter(CartItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            cart_item_id: int
    ) -> CartItemModel:
        with self.order_database() as order_db:
            cart_item = order_db.delete_from_shopping_bag(
                payload.sub,
                cart_item_id
            )

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect item_id"
            )

        return self.converter.serialization(cart_item)[0]


class CartItemLoader(BaseDependency):
    """Загрузка карточек товаров в корзине"""

    def __init__(
            self,
            converter: Converter = Converter(CartItemCardModel)
    ):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_item_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CartItemCardListModel:
        """
        :param amount: требуемое количество карточек
        :param last_item_id: id карточки из последней подгрузки;
                             если это первый запрос на получение карточек,
                             оставить None

        :return: список из карточек товаров
        """

        try:
            with self.order_database() as order_db:
                cart_items = order_db.get_cart(
                    user_id=payload.sub,
                    amount=amount,
                    last_item_id=last_item_id
                )

            return CartItemCardListModel(
                cart_items=self.converter.serialization(cart_items)
            )

        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


# dependencies
add_to_cart_dependency = CartItemSaver()
delete_from_cart_dependency = CartItemDeleter()
get_cart_dependency = CartItemLoader()
