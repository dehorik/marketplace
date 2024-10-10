import smtplib

from core.settings import config


class EmailSender:
    def __init__(
            self,
            sender_address: str = config.SENDER_ADDRESS,
            sender_password: str = config.SENDER_PASSWORD,
            host: str = config.SMTP_SERVER_HOST,
            port: int = config.SMTP_SERVER_PORT
    ):
        server = smtplib.SMTP(host=host, port=port)
        server.starttls()
        server.login(sender_address, sender_password)

        self.__server = server
        self.__sender_address = sender_address

    def send_mail(self, message: str, receiver: str) -> None:
        self.__server.sendmail(self.__sender_address, receiver, message)


# email_sender = EmailSender(
#     config.SENDER_ADDRESS,
#     config.SENDER_PASSWORD,
#     config.SMTP_SERVER_HOST,
#     config.SMTP_SERVER_PORT
# )
# email_sender.send_mail("the first message", "dondinles2@gmail.com")
