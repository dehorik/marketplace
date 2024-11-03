import os
from typing import Callable
from datetime import UTC, datetime, timedelta
from jinja2 import Environment, FileSystemLoader

from auth import JWTEncoder, get_jwt_encoder
from core.tasks.models import EmailTokenPayloadModel, OrderNotificationModel
from core.database import (
    CommentDataAccessObject,
    OrderDataAccessObject,
    get_comment_dao,
    get_order_dao
)
from core.settings import ROOT_PATH
from utils import (
    Converter,
    EmailSender,
    get_email_sender,
    exists,
    delete_file
)


class EmailVerificationTask:
    def __init__(
            self,
            jwt_encoder: JWTEncoder = get_jwt_encoder(),
            email_sender: EmailSender = get_email_sender()
    ):
        self.jwt_encoder = jwt_encoder
        self.email_sender = email_sender

    def __call__(self, user_id: int, email: str, username: str) -> None:
        iat = datetime.now(UTC)
        exp = iat + timedelta(minutes=30)
        payload = EmailTokenPayloadModel(
            sub=user_id,
            email=email,
            iat=iat,
            exp=exp
        )
        payload = payload.model_dump()
        token = self.jwt_encoder(payload)

        loader = FileSystemLoader(os.path.join(ROOT_PATH, r"frontend\templates"))
        env = Environment(loader=loader)
        template = env.get_template("email_verification_letter.html")
        letter = template.render(
            token=token,
            username=username,
            year=datetime.now().year
        )

        self.email_sender.send_letter(email, "Подтверждение почты", letter)


class OrderNotificationTask:
    def __init__(
            self,
            subject: str,
            template_name: str,
            email_sender: EmailSender = get_email_sender(),
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(OrderNotificationModel)
    ):
        self.subject = subject
        self.template_name = template_name
        self.email_sender = email_sender
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(self, order_id: int) -> None:
        order = self.order_data_access_obj.get_order_notification_data(order_id)
        order = self.converter.fetchone(order)

        if not order.email:
            return

        order.date_start = order.date_start.strftime("%d.%m.%Y %H:%M")
        order.date_end = order.date_end.strftime("%d.%m.%Y %H:%M")

        loader = FileSystemLoader(os.path.join(ROOT_PATH, r"frontend\templates"))
        env = Environment(loader=loader)
        template = env.get_template(self.template_name)
        letter = template.render(order=order, year=datetime.now().year)

        self.email_sender.send_letter(order.email, self.subject, letter)


class CommentsRemovalTask:
    def __init__(
            self,
            comment_dao: CommentDataAccessObject = get_comment_dao(),
            file_deleter: Callable = delete_file
    ):
        self.comment_data_access_obj = comment_dao
        self.file_deleter = file_deleter

    def __call__(self) -> None:
        comments = self.comment_data_access_obj.delete_undefined_comments()

        for comment in comments:
            photo_path = comment[-1]

            if photo_path and exists(photo_path):
                self.file_deleter(photo_path)


class OrdersRemovalTask:
    def __init__(
            self,
            order_dao: OrderDataAccessObject = get_order_dao(),
            file_deleter: Callable = delete_file
    ):
        self.order_data_access_obj = order_dao
        self.file_deleter = file_deleter

    def __call__(self) -> None:
        orders = self.order_data_access_obj.delete_undefined_orders()

        for order in orders:
            photo_path = order[-1]

            if photo_path and exists(photo_path):
                self.file_deleter(photo_path)


email_verification_task = EmailVerificationTask()
order_creation_notification_task = OrderNotificationTask(
    subject="Новый заказ",
    template_name="order_creation_letter.html"
)
order_update_notification_task = OrderNotificationTask(
    subject="Изменение заказа",
    template_name="order_update_letter.html"
)
comments_removal_task = CommentsRemovalTask()
orders_removal_task = OrdersRemovalTask()
