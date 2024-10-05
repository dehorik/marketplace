from typing import List
from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    """Базовая схема товара"""

    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)
    product_description: str = Field(min_length=2, max_length=300)
    is_hidden: bool = False
    photo_path: str


class ExtendedProductModel(BaseModel):
    """Расширенная схема товара с дополнительными полями"""

    product_data: ProductModel
    product_rating: float | None = Field(ge=1, le=5, default=None)
    amount_comments: int


class ProductCardModel(BaseModel):
    """Схема карточки товара в каталоге"""

    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)
    product_rating: float | None = Field(ge=1, le=5, default=None)
    photo_path: str


class ProductCardListModel(BaseModel):
    products: List[ProductCardModel]
