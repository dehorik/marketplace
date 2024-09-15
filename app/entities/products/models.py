from typing import List
from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    """Базовая схема товара"""

    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)
    product_description: str = Field(min_length=2, max_length=300)
    product_photo_path: str


class ExtendedProductModel(BaseModel):
    """
    Расширенная схема товара с дополнительными полями.
    Например, для получения рейтинга и т.д
    """

    product: ProductModel
    product_rating: float | None = Field(ge=1, le=5, default=None)
    amount_comments: int


class ProductCatalogCardModel(BaseModel):
    """Схема карточки товара в каталоге"""

    product_id: int
    product_name: str = Field(min_length=2, max_length=20)
    product_price: int = Field(gt=0, le=100000)
    product_rating: float | None = Field(ge=1, le=5, default=None)
    product_photo_path: str


class ProductCatalogModel(BaseModel):
    products: List[ProductCatalogCardModel]
