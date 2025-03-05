import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.settings import config


class EmailSender:
    """
    Класс для отправки писем по электронной почте.
    Письма можно отправлять только при использовании контекстного менеджера.

    with EmailSender("your_email@example.com", "password", "smtp.example.com", 587) as sender:
        sender.send_letter("recipient@example.com", "Subject", "<h1>Hello</h1>")
    """

    def __init__(
            self,
            sender_address: str,
            sender_password: str,
            host: str,
            port: int
    ):
        """
        :param sender_address: адрес электронной почты отправителя
        :param sender_password: пароль от почты отправителя
        :param host: smtp сервер.
        :param port: порт smtp сервера
        """

        self.__sender_address = sender_address
        self.__sender_password = sender_password
        self.__host = host
        self.__port = port
        self.__server = None

    def __enter__(self):
        """Устанавливает соединение с smtp сервером"""

        self.__server = smtplib.SMTP(host=self.__host, port=self.__port)
        self.__server.starttls()
        self.__server.login(self.__sender_address, self.__sender_password)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает соединение с smtp сервером"""

        if self.__server:
            self.__server.quit()
            self.__server = None

    def __get_letter(
            self,
            receiver_address: str,
            subject: str,
            html: str
    ) -> MIMEMultipart:
        """
        Создаёт письмо в формате html.

        :param receiver_address: адрес электронной почты получателя
        :param subject: тема письма
        :param html: тело письма в формате html
        :return: готовое письмо
        """

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
        """
        :param receiver_address: адрес электронной почты получателя
        :param subject: тема письма
        :param html: тело письма в формате html
        :raises ConnectionError: если объект не используется в with и сервер не инициализирован
        """

        if self.__server:
            letter = self.__get_letter(receiver_address, subject, html)
            self.__server.send_message(letter)
        else:
            raise ConnectionError("SMTP server not initialized")


def get_email_sender() -> EmailSender:
    return EmailSender(
        config.SENDER_ADDRESS,
        config.SENDER_PASSWORD,
        config.SMTP_SERVER_HOST,
        config.SMTP_SERVER_PORT
    )
