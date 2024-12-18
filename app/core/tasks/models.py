from datetime import datetime
from pydantic import BaseModel, EmailStr


class EmailTokenPayloadModel(BaseModel):
    sub: int
    email: EmailStr
    iat: datetime
    exp: datetime


class OrderNotificationModel(BaseModel):
    order_id: int
    product_name: str
    product_price: int
    date_start: datetime | str
    date_end: datetime | str
    delivery_address: str
    username: str
    email: str | None
