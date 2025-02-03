from typing import List
from datetime import date
from pydantic import BaseModel


class CommentModel(BaseModel):
    """Базовая схема отзыва"""

    comment_id: int
    user_id: int
    product_id: int
    rating: int
    creation_date: date
    text: str | None
    has_photo: bool


class CommentItemModel(BaseModel):
    """Схема отзыва, подгружаемого на страницу с отзывами"""

    comment_id: int
    user_id: int
    product_id: int
    username: str
    user_has_photo: bool
    rating: int
    creation_date: date
    text: str | None
    comment_has_photo: bool


class CommentItemListModel(BaseModel):
    comments: List[CommentItemModel]
