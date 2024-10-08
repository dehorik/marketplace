from typing import Type, Annotated
from fastapi import HTTPException, Depends, Query, status
from psycopg2.errors import ForeignKeyViolation

from entities.orders.models import (
    CartItemModel,
    CartItemCardModel,
    CartItemCardListModel
)
from auth import AuthorizationService, PayloadTokenModel
from core.database import OrderDataBase
from utils import Converter


base_user_dependency = AuthorizationService(min_role_id=1)


class BaseDependency:
    def __init__(
            self,
            order_database: Type[OrderDataBase] = OrderDataBase
    ):
        self.order_database = order_database


class CartItemSaveService(BaseDependency):
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
                cart_item = order_db.add_to_cart(payload.sub, product_id)

            return self.converter(cart_item)[0]
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


class CartItemRemovalService(BaseDependency):
    """Удаление товара из корзины"""

    def __init__(self, converter: Converter = Converter(CartItemModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(base_user_dependency)],
            item_id: int
    ) -> CartItemModel:
        with self.order_database() as order_db:
            cart_item = order_db.delete_from_cart(payload.sub, item_id)

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect item_id"
            )

        return self.converter(cart_item)[0]


class CartItemLoaderService(BaseDependency):
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
        :param last_item_id: cart_item_id карточки товара в корзине из
                             последней подгрузки (если это первый запрос
                             на получение карточек - оставить None)
        """

        try:
            with self.order_database() as order_db:
                cart_items = order_db.get_cart(
                    user_id=payload.sub,
                    amount=amount,
                    last_item_id=last_item_id
                )

            return CartItemCardListModel(
                cart_items=self.converter(cart_items)
            )

        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )


# dependencies
cart_item_save_service = CartItemSaveService()
cart_item_removal_service = CartItemRemovalService()
cart_item_loader_service = CartItemLoaderService()
