import os
from typing import Callable
from datetime import UTC, datetime, timedelta
from jinja2 import Environment, FileSystemLoader


from auth import JWTEncoder, get_jwt_encoder
from core.tasks.models import EmailTokenPayloadModel, OrderLetterDataModel
from core.database import (
    CommentDataAccessObject,
    OrderDataAccessObject,
    get_comment_dao,
    get_order_dao
)
from core.settings import ROOT_PATH
from utils import EmailSender, get_email_sender, delete_file, Converter


class EmailVerificationTask:
    def __init__(
            self,
            jwt_encoder: JWTEncoder = get_jwt_encoder(),
            email_sender: EmailSender = get_email_sender()
    ):
        self.jwt_encoder = jwt_encoder
        self.email_sender = email_sender

    def __call__(self, user_id: int, email: str) -> None:
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
        letter = template.render(token=token, year=datetime.now().year)

        self.email_sender.send_letter(email, "Подтверждение почты", letter)


class ProductRemovalTask:
    def __init__(
            self,
            file_deleter: Callable = delete_file,
            comment_dao: CommentDataAccessObject = get_comment_dao()
    ):
        self.file_deleter = file_deleter
        self.comment_data_access_obj = comment_dao

    def __call__(self) -> None:
        comments = self.comment_data_access_obj.delete_undefined_comments()

        for comment in comments:
            photo_path = comment[-1]

            if photo_path:
                self.file_deleter(photo_path)


class OrderNotificationTask:
    def __init__(
            self,
            email_sender: EmailSender = get_email_sender(),
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(OrderLetterDataModel)
    ):
        self.email_sender = email_sender
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(self, order_id: int) -> None:
        order = self.order_data_access_obj.get_order_letter_data(order_id)
        order = self.converter(order)[0]

        if not order.email:
            return

        date_start = order.date_start.strftime("%d-%m-%Y %H:%M").replace("-", ".")
        date_end = order.date_start.strftime("%d-%m-%Y %H:%M").replace("-", ".")
        order.date_start = date_start
        order.date_end = date_end

        loader = FileSystemLoader(os.path.join(ROOT_PATH, r"frontend\templates"))
        env = Environment(loader=loader)
        template = env.get_template("order_creation_letter.html")
        letter = template.render(order=order, year=datetime.now().year)

        self.email_sender.send_letter(order.email, "Новый заказ", letter)


email_verification_task = EmailVerificationTask()
product_removal_task = ProductRemovalTask()
order_notification_task = OrderNotificationTask()
