from typing import List
from datetime import datetime
from pydantic import BaseModel


class CommentModel(BaseModel):
    """Базовая схема отзыва"""

    comment_id: int
    user_id: int
    product_id: int
    rating: int
    creation_date: datetime
    text: str | None
    photo_path: str | None


class CommentItemModel(BaseModel):
    """Схема отзыва, подгружаемого на страницу с отзывами"""

    comment_id: int
    user_id: int
    product_id: int
    username: str
    user_photo_path: str | None
    rating: int
    creation_date: datetime
    text: str | None
    comment_photo_path: str | None


class CommentItemListModel(BaseModel):
    comments: List[CommentItemModel]
