from random import randint
from typing import Annotated
from datetime import UTC, datetime, timedelta
from fastapi import Form, Query, Path
from fastapi import HTTPException, BackgroundTasks, Depends, status
from psycopg2.errors import ForeignKeyViolation, RaiseException

from entities.orders.models import (
    CartItemCreationRequest,
    CartItemModel,
    CartItemCardModel,
    CartItemCardListModel,
    OrderModel
)
from auth import AuthorizationService, TokenPayloadModel
from core.tasks import order_notification_task
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
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            data: CartItemCreationRequest
    ) -> CartItemModel:
        try:
            cart_item = self.order_data_access_obj.craete_cart_item(
                payload.sub,
                data.product_id
            )
            cart_item = self.converter.fetchone(cart_item)

            return cart_item
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )


class CartItemLoadService:
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
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CartItemCardListModel:
        """
        :param amount: требуемое количество карточек
        :param last_id: id карточки товара в корзине
               из последней подгрузки (если это первый запрос - None)
        """

        cart_items = self.order_data_access_obj.get_cart_items(
            user_id=payload.sub,
            amount=amount,
            last_id=last_id
        )
        cart_items = self.converter.fetchmany(cart_items)

        return CartItemCardListModel(cart_items=cart_items)


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
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            cart_item_id: Annotated[int, Path(ge=1)]
    ) -> CartItemModel:
        try:
            cart_item = self.order_data_access_obj.delete_cart_item(
                cart_item_id,
                payload.sub
            )
            cart_item = self.converter.fetchone(cart_item)

            return cart_item
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="cart item not found"
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
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
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

            background_tasks.add_task(
                order_notification_task,
                order.order_id
            )

            return order
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="product not found"
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )


cart_item_creation_service = CartItemCreationService()
cart_item_load_service = CartItemLoadService()
cart_item_removal_service = CartItemRemovalService()
order_creation_service = OrderCreationService()
