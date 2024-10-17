import os
import datetime
from typing import Type, Callable
from jinja2 import Environment, FileSystemLoader

from core.tasks.models import EmailTokenPayloadModel
from auth import JWTEncoder
from core.database import CommentDataAccessObject
from core.settings import ROOT_PATH
from utils import EmailSender, create_email_sender_obj, delete_file


class EmailSendingTask:
    def __init__(
            self,
            jwt_encoder: JWTEncoder = JWTEncoder(),
            email_sender: EmailSender = create_email_sender_obj()
    ):
        self.jwt_encoder = jwt_encoder
        self.email_sender = email_sender

    def __call__(self, user_id: int, email: str) -> None:
        iat = datetime.datetime.now(datetime.UTC)
        exp = iat + datetime.timedelta(minutes=30)
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
        letter = template.render(token=token)

        self.email_sender.send_letter(email, "Подтверждение почты", letter)


class ProductRemovalTask:
    def __init__(
            self,
            file_deleter: Callable = delete_file,
            comment_dao: Type[CommentDataAccessObject] = CommentDataAccessObject
    ):
        self.file_deleter = file_deleter
        self.comment_dao = comment_dao

    def __call__(self) -> None:
        with self.comment_dao() as comment_data_access_obj:
            comments = comment_data_access_obj.delete_undefined_comments()

        for comment in comments:
            photo_path = comment[-1]

            if photo_path:
                self.file_deleter(photo_path)


email_sending_task = EmailSendingTask()
product_removal_task = ProductRemovalTask()
