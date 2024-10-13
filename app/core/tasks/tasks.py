import os
import datetime
from jinja2 import Environment, FileSystemLoader

from auth import JWTEncoder
from core.tasks.models import EmailTokenPayloadModel
from core.settings import ROOT_PATH
from utils import EmailSender, create_email_sender_obj


class EmailSendingService:
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


email_sending_service = EmailSendingService()
