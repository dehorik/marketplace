import smtplib

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

    def __del__(self):
        self.__server.quit()

    def send_mail(self, message: str, receiver: str) -> None:
        self.__server.sendmail(self.__sender_address, receiver, message)


def create_email_sender_obj() -> EmailSender:
    return EmailSender(
        config.SENDER_ADDRESS,
        config.SENDER_PASSWORD,
        config.SMTP_SERVER_HOST,
        config.SMTP_SERVER_PORT
    )
