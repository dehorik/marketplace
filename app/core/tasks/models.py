from datetime import datetime
from pydantic import BaseModel, EmailStr


class EmailTokenPayloadModel(BaseModel):
    sub: int
    email: EmailStr
    iat: datetime
    exp: datetime
