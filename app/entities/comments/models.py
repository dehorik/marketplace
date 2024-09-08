from typing import List
from datetime import datetime
from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    """Базовая схема отзыва"""

    comment_id: int
    user_id: int
    product_id: int
    comment_rating: int = Field(ge=1, le=5)
    comment_date: datetime
    comment_text: str | None = Field(min_length=2, max_length=100, default=None)
    comment_photo_path: str | None = None


class CommentItemModel(BaseModel):
    """Схема отзыва, подгружаемого на страницу с отзывами"""

    comment_id: int
    user_id: int
    product_id: int
    user_name: str
    user_photo_path: str | None = None
    comment_rating: int = Field(ge=1, le=5)
    comment_date: datetime
    comment_text: str | None = Field(min_length=2, max_length=100, default=None)
    comment_photo_path: str | None = None


class CommentItemListModel(BaseModel):
    comments: List[CommentItemModel]
