from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    user_id: int
    role_id: int
    username: str = Field(min_length=6, max_length=16)
    email: EmailStr | None = None
    photo_path: str | None = None
