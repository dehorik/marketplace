import os
from random import randint
from typing import Annotated, Callable
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException, BackgroundTasks, Depends, Query, Path, status
from psycopg2.errors import ForeignKeyViolation, RaiseException

from core.settings import config
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
from utils import Converter, copy_file, delete_file


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class OrderCreationService:
    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(OrderModel),
            file_copier: Callable = copy_file
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter
        self.file_copier = file_copier

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            data: OrderCreationRequest
    ) -> OrderModel:
        try:
            now = datetime.now(UTC)
            delta = timedelta(
                days=randint(0, 3),
                hours=randint(0, 24),
                minutes=randint(0, 60)
            )
            date_end = now + delta
            order = self.order_data_access_obj.create(
                payload.sub,
                data.product_id,
                date_end,
                data.delivery_address
            )
            order = self.converter.fetchone(order)

            product_photo_path = os.path.join(
                config.PRODUCT_CONTENT_PATH,
                str(data.product_id)
            )
            background_tasks.add_task(
                self.file_copier,
                product_photo_path, order.photo_path
            )

            background_tasks.add_task(
                order_creation_notification_task,
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


class OrderLoadService:
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
            now = datetime.now(UTC)
            delta = timedelta(
                days=randint(0, 3),
                hours=randint(0, 24),
                minutes=randint(0, 60)
            )
            date_end = now + delta
            order = self.order_data_access_obj.update(
                order_id,
                payload.sub,
                date_end,
                data.delivery_address
            )
            order = self.converter.fetchone(order)

            background_tasks.add_task(
                order_update_notification_task,
                order.order_id
            )

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
            file_deleter: Callable = delete_file
    ):
        self.order_data_access_obj = order_dao
        self.converter = converter
        self.file_deleter = file_deleter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            order_id: Annotated[int, Path(ge=1)]
    ) -> OrderModel:
        try:
            order = self.order_data_access_obj.delete(order_id, payload.sub)
            order = self.converter.fetchone(order)

            background_tasks.add_task(
                self.file_deleter,
                order.photo_path
            )

            return order
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="order not found"
            )


order_creation_service = OrderCreationService()
order_load_service = OrderLoadService()
order_update_service = OrderUpdateService()
order_deletion_service = OrderDeletionService()
