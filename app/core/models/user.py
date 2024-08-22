from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    user_id: int
    role_id: int
    user_name: str = Field(min_length=6, max_length=18)
    user_email: EmailStr | None = Field(default=None)
    user_photo_path: str | None = Field(default=None)

