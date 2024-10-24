import os
import datetime
from typing import Callable
from jinja2 import Environment, FileSystemLoader

from core.tasks.models import EmailTokenPayloadModel
from auth import JWTEncoder, get_jwt_encoder
from core.database import CommentDataAccessObject, get_comment_dao
from core.settings import ROOT_PATH
from utils import EmailSender, get_email_sender, delete_file


class EmailSendingTask:
    def __init__(
            self,
            jwt_encoder: JWTEncoder = get_jwt_encoder(),
            email_sender: EmailSender = get_email_sender()
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


email_sending_task = EmailSendingTask()
product_removal_task = ProductRemovalTask()
