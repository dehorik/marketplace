from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    user_id: int
    role_id: int
    user_name: str = Field(min_length=6, max_length=14)
    user_email: EmailStr | None = None
    user_photo_path: str | None = None
