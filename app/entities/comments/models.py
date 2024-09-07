from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    comment_id: int
    user_id: int
    product_id: int
    comment_date: datetime
    comment_text: str | None = Field(min_length=3, max_length=100, default=None)
    comment_rating: int = Field(ge=1, le=5)
    comment_photo_path: str | None = None


class CommentItemModel(BaseModel):
    comment_id: int
    user_id: int
    product_id: int
    user_name: str
    user_photo_path: str | None = None
    comment_date: datetime
    comment_text: str | None = None
    comment_rating: int
    comment_photo_path: str | None = None


class CommentItemListModel(BaseModel):
    comments: List[CommentItemModel]
