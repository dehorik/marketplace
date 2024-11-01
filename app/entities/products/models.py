from typing import List
from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    """Базовая схема товара"""

    product_id: int
    name: str = Field(min_length=2, max_length=20)
    price: int = Field(gt=0, le=100000)
    description: str = Field(min_length=2, max_length=300)
    is_hidden: bool
    amount_orders: int
    photo_path: str


class ExtendedProductModel(BaseModel):
    """Расширенная схема товара с дополнительными полями"""

    product_id: int
    name: str = Field(min_length=2, max_length=20)
    price: int = Field(gt=0, le=100000)
    description: str = Field(min_length=2, max_length=300)
    is_hidden: bool
    amount_orders: int
    photo_path: str
    rating: float | None = Field(ge=1, le=5, default=None)
    amount_comments: int


class ProductCardModel(BaseModel):
    """Схема карточки товара в каталоге"""

    product_id: int
    name: str = Field(min_length=2, max_length=20)
    price: int = Field(gt=0, le=100000)
    rating: float | None = Field(ge=1, le=5, default=None)
    photo_path: str


class ProductCardListModel(BaseModel):
    products: List[ProductCardModel]
