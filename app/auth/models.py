from pydantic import BaseModel, Field


class Credentials(BaseModel):
    user_name: str = Field(min_length=6, max_length=14)
    user_password: str = Field(min_length=8, max_length=18)
