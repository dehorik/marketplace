from typing import List
from datetime import datetime
from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    """Базовая схема отзыва"""

    comment_id: int
    user_id: int
    product_id: int
    rating: int = Field(ge=1, le=5)
    creation_date: datetime
    text: str | None = Field(default=None, min_length=2, max_length=200)
    photo_path: str | None = None


class CommentItemModel(BaseModel):
    """Схема отзыва, подгружаемого на страницу с отзывами"""

    comment_id: int
    user_id: int
    product_id: int
    username: str = Field(min_length=6, max_length=16)
    user_photo_path: str | None = None
    rating: int = Field(ge=1, le=5)
    creation_date: datetime
    text: str | None = Field(default=None, min_length=2, max_length=200)
    comment_photo_path: str | None = None


class CommentItemListModel(BaseModel):
    comments: List[CommentItemModel]
