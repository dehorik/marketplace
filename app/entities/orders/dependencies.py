from random import randint
from typing import Annotated
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException, BackgroundTasks, Depends, Query, Form, status
from psycopg2.errors import ForeignKeyViolation, RaiseException

from entities.orders.models import (
    CartItemModel,
    CartItemCardModel,
    CartItemCardListModel,
    OrderModel,
)
from core.tasks import order_notification_task
from auth import PayloadTokenModel, AuthorizationService
from core.database import OrderDataAccessObject, get_order_dao
from utils import Converter


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class CartItemCreationService:
    """Добавление товара в корзину"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(CartItemModel)
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(user_dependency)],
            product_id: int
    ) -> CartItemModel:
        try:
            cart_item = self.order_data_access_obj.add_to_cart(
                payload.sub,
                product_id
            )

            return self.converter.fetchone(cart_item)
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )


class CartItemRemovalService:
    """Удаление товара из корзины"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(CartItemModel)
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(user_dependency)],
            item_id: int
    ) -> CartItemModel:
        try:
            cart_item = self.order_data_access_obj.delete_from_cart(
                payload.sub,
                item_id
            )

            return self.converter.fetchone(cart_item)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="cart item not found"
            )


class CartItemLoaderService:
    """Загрузка карточек товаров в корзине"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(CartItemCardModel)
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[PayloadTokenModel, Depends(user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_item_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CartItemCardListModel:
        """
        :param amount: требуемое количество карточек
        :param last_item_id: cart_item_id карточки товара в корзине
               из последней подгрузки (если это первый запрос - None)
        """

        cart_items = self.order_data_access_obj.get_cart(
            user_id=payload.sub,
            amount=amount,
            last_item_id=last_item_id
        )

        return CartItemCardListModel(
            cart_items=self.converter.fetchmany(cart_items)
        )


class OrderCreationService:
    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(OrderModel)
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[PayloadTokenModel, Depends(user_dependency)],
            product_id: Annotated[int, Form(ge=1)],
            delivery_address: Annotated[str, Form(min_length=6, max_length=30)]
    ) -> OrderModel:
        try:
            now = datetime.now(UTC)
            date_end = now + timedelta(days=randint(1, 3))
            order = self.order_data_access_obj.create(
                payload.sub,
                product_id,
                date_end,
                delivery_address
            )
            order = self.converter.fetchone(order)

            background_tasks.add_task(order_notification_task, order.order_id)

            return order
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="the product cannot be ordered"
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )


# dependencies
cart_item_creation_service = CartItemCreationService()
cart_item_removal_service = CartItemRemovalService()
cart_item_loader_service = CartItemLoaderService()
order_creation_service = OrderCreationService()
