from datetime import datetime
from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    comment_id: int
    user_id: int
    product_id: int
    comment_date: datetime
    comment_text: str | None = Field(min_length=3, max_length=200, default=None)
    comment_rating: int = Field(ge=1, le=5)
    comment_photo_path: str | None = None
