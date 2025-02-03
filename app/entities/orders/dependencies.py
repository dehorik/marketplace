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
    OrderCardModel,
    OrderCardListModel
)
from auth import AuthorizationService, TokenPayloadModel
from core.tasks import (
    order_creation_notification_task,
    order_update_notification_task
)
from core.database import OrderDataAccessObject, get_order_dao
from utils import Converter, FileRemover
from core.settings import ROOT_PATH


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


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
    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(OrderCardModel)
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 9,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> OrderCardListModel:
        orders = self.order_data_access_obj.read(
            user_id=payload.sub,
            amount=amount,
            last_id=last_id
        )
        orders = self.converter.fetchmany(orders)

        return OrderCardListModel(orders=orders)


class OrderUpdateService:
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
    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(OrderModel),
            file_remover: FileRemover = FileRemover(join("images", "orders"))
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


order_creation_service = OrderCreationService()
fetch_orders_service = FetchOrdersService()
order_update_service = OrderUpdateService()
order_deletion_service = OrderDeletionService()
