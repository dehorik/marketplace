from os.path import join
from random import randint
from shutil import copy
from typing import Annotated
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, BackgroundTasks, Depends, Query, Path, status
from psycopg2.errors import ForeignKeyViolation

from entities.orders.models import (
    OrderCreationRequest,
    OrderUpdateRequest,
    OrderModel,
    OrderListModel
)
from auth import user_dependency, TokenPayloadModel
from core.tasks import (
    order_creation_notification_task,
    order_update_notification_task
)
from core.database import OrderDataAccessObject, get_order_dao
from utils import Converter, FileRemover
from core.settings import ROOT_PATH


class OrderCreationService:
    """Создание заказа"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject,
            converter: Converter
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            data: OrderCreationRequest
    ) -> OrderModel:
        try:
            order = self.order_data_access_obj.create(
                payload.sub,
                data.product_id,
                datetime.now(timezone.utc).date(),
                datetime.now(timezone.utc).date() + timedelta(days=randint(1, 2)),
                data.delivery_address
            )
            order = self.converter.fetchone(order)

            copy(
                join(ROOT_PATH, "images", "products", f"{order.product_id}.jpg"),
                join(ROOT_PATH, "images", "orders", f"{order.order_id}.jpg")
            )

            background_tasks.add_task(order_creation_notification_task, order.order_id)

            return order
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )


class FetchOrdersService:
    """Получение последних заказов пользователя"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject,
            converter: Converter
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 15,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> OrderListModel:
        """
        :param amount: количество заказов
        :param last_id: order_id последнего подгруженного заказа
        """

        orders = self.order_data_access_obj.read(
            user_id=payload.sub,
            amount=amount,
            last_id=last_id
        )
        orders = self.converter.fetchmany(orders)

        return OrderListModel(orders=orders)


class OrderUpdateService:
    """Обновление данных заказа"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject,
            converter: Converter
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            order_id: Annotated[int, Path(ge=1)],
            data: OrderUpdateRequest
    ) -> OrderModel:
        try:
            order = self.order_data_access_obj.update(
                order_id,
                payload.sub,
                datetime.now(timezone.utc).date() + timedelta(days=randint(2, 3)),
                data.delivery_address
            )
            order = self.converter.fetchone(order)

            background_tasks.add_task(order_update_notification_task, order.order_id)

            return order
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="order not found"
            )


class OrderDeletionService:
    """Удаление заказа"""

    def __init__(
            self,
            order_dao: OrderDataAccessObject,
            converter: Converter,
            file_remover: FileRemover
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter
        self.file_remover = file_remover

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            order_id: Annotated[int, Path(ge=1)]
    ) -> OrderModel:
        try:
            order = self.order_data_access_obj.delete(order_id, payload.sub)
            order = self.converter.fetchone(order)

            self.file_remover(order.order_id)

            return order
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="order not found"
            )


order_creation_service = OrderCreationService(
    order_dao=get_order_dao(),
    converter=Converter(OrderModel)
)

fetch_orders_service = FetchOrdersService(
    order_dao=get_order_dao(),
    converter=Converter(OrderModel)
)

order_update_service = OrderUpdateService(
    order_dao=get_order_dao(),
    converter=Converter(OrderModel)
)

order_deletion_service = OrderDeletionService(
    order_dao=get_order_dao(),
    converter=Converter(OrderModel),
    file_remover=FileRemover(join("images", "orders"))
)
