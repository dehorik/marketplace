from datetime import datetime
from pydantic import BaseModel, EmailStr


class EmailTokenPayloadModel(BaseModel):
    sub: int
    email: EmailStr
    iat: datetime
    exp: datetime


class OrderNotificationModel(BaseModel):
    order_id: int
    date_start: datetime | str
    date_end: datetime | str
    delivery_address: str
    username: str
    email: str | None
    product_name: str
    price: int
