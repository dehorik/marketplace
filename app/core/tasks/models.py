from datetime import date, datetime
from pydantic import BaseModel, EmailStr


class EmailTokenPayloadModel(BaseModel):
    """Схема jwt, хранящего данные для подтверждения почты"""

    sub: int
    email: EmailStr
    iat: datetime
    exp: datetime


class OrderNotificationModel(BaseModel):
    """Схема данных о заказе для формирования письма"""

    order_id: int
    product_name: str
    product_price: int
    date_start: date | str
    date_end: date | str
    delivery_address: str
    username: str
    email: str | None
