from os.path import join
from datetime import UTC, datetime, timedelta, timezone
from jinja2 import Environment, FileSystemLoader

from auth import JWTEncoder, get_jwt_encoder
from core.tasks.models import OrderNotificationModel
from core.database import (
    CommentDataAccessObject,
    OrderDataAccessObject,
    get_comment_dao,
    get_order_dao
)
from core.settings import ROOT_PATH
from utils import Converter, FileRemover, EmailSender, get_email_sender


class EmailVerificationTask:
    """Задача отправки письма для подтверждения почты"""

    def __init__(
            self,
            jwt_encoder: JWTEncoder,
            email_sender: EmailSender
    ):
        self.jwt_encoder = jwt_encoder
        self.email_sender = email_sender

    def __call__(self, user_id: int, email: str, username: str) -> None:
        iat = datetime.now(UTC)
        exp = iat + timedelta(minutes=30)
        payload = {
            "sub": user_id,
            "email": email,
            "iat": iat,
            "exp": exp
        }
        token = self.jwt_encoder(payload)

        loader = FileSystemLoader(join(ROOT_PATH, "frontend", "templates"))
        env = Environment(loader=loader)
        template = env.get_template("email-verification-letter.html")
        letter = template.render(token=token, username=username, year=datetime.now().year)

        with self.email_sender as sender:
            sender.send_letter(email, "Подтверждение почты", letter)


class OrderNotificationTask:
    """Задача почтового уведомления о создании или изменении заказа"""

    def __init__(
            self,
            subject: str,
            template_name: str,
            email_sender: EmailSender,
            order_dao: OrderDataAccessObject,
            converter: Converter
    ):
        # subject - тема письма
        # template_name - имя html шаблона письма

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

        order.date_start = order.date_start.strftime("%d.%m.%Y")
        order.date_end = order.date_end.strftime("%d.%m.%Y")

        loader = FileSystemLoader(join(ROOT_PATH, "frontend", "templates"))
        env = Environment(loader=loader)
        template = env.get_template(self.template_name)
        letter = template.render(order=order, year=datetime.now(timezone.utc).date().year)

        with self.email_sender as sender:
            sender.send_letter(order.email, self.subject, letter)


class CommentsRemovalTask:
    """
    Задача удаления всех неопределенных отзывов.
    Отзыв считается неопределенным, если поля внешних ключей
    (user_id или product_id) ссылаются на NULL
    """

    def __init__(
            self,
            comment_dao: CommentDataAccessObject,
            file_remover: FileRemover
    ):
        self.comment_data_access_obj = comment_dao
        self.file_remover = file_remover

    def __call__(self) -> None:
        comments = self.comment_data_access_obj.delete_undefined_comments()

        for comment in comments:
            self.file_remover(comment[0])


class OrdersRemovalTask:
    """
    Задача удаления всех неопределенных заказов.
    Заказ считается неопределенным, если поля внешних ключей
    (user_id или product_id) ссылаются на NULL
    """

    def __init__(
            self,
            order_dao: OrderDataAccessObject,
            file_remover: FileRemover
    ):
        self.order_data_access_obj = order_dao
        self.file_remover = file_remover

    def __call__(self) -> None:
        orders = self.order_data_access_obj.delete_undefined_orders()

        for order in orders:
            self.file_remover(order[0])


email_verification_task = EmailVerificationTask(
    jwt_encoder=get_jwt_encoder(),
    email_sender=get_email_sender()
)

order_creation_notification_task = OrderNotificationTask(
    subject="Новый заказ",
    template_name="order-creation-letter.html",
    email_sender=get_email_sender(),
    order_dao=get_order_dao(),
    converter=Converter(OrderNotificationModel)
)

order_update_notification_task = OrderNotificationTask(
    subject="Изменение заказа",
    template_name="order-update-letter.html",
    email_sender=get_email_sender(),
    order_dao=get_order_dao(),
    converter=Converter(OrderNotificationModel)
)

comments_removal_task = CommentsRemovalTask(
    comment_dao=get_comment_dao(),
    file_remover=FileRemover(join("images", "comments"))
)

orders_removal_task = OrdersRemovalTask(
    order_dao=get_order_dao(),
    file_remover=FileRemover(join("images", "orders"))
)
