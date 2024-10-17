import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.settings import config


class EmailSender:
    def __init__(
            self,
            sender_address: str,
            sender_password: str,
            host: str,
            port: int
    ):
        server = smtplib.SMTP(host=host, port=port)
        server.starttls()
        server.login(sender_address, sender_password)

        self.__server = server
        self.__sender_address = sender_address

    def __get_letter(
            self,
            receiver_address: str,
            subject: str,
            html: str
    ) -> MIMEMultipart:
        letter = MIMEMultipart("alternative")
        letter["Subject"] = subject
        letter["From"] = self.__sender_address
        letter["To"] = receiver_address
        letter.attach(MIMEText(html, "html"))

        return letter

    def send_letter(
            self,
            receiver_address: str,
            subject: str,
            html: str
    ) -> None:
        letter = self.__get_letter(receiver_address, subject, html)
        self.__server.send_message(letter)


def get_email_sender() -> EmailSender:
    return EmailSender(
        config.SENDER_ADDRESS,
        config.SENDER_PASSWORD,
        config.SMTP_SERVER_HOST,
        config.SMTP_SERVER_PORT
    )
