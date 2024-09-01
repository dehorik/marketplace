from typing import List
from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    product_id: int
    user_id: int
    product_name: str = Field(min_length=2, max_length=30)
    product_price: float = Field(gt=0, le=1000000)
    product_description: str = Field(min_length=2, max_length=300)
    product_ratig: float | None = Field(ge=1, le=5, default=None)
    product_photo_path: str


class ProductCatalogCardModel(BaseModel):
    product_id: int
    product_name: str = Field(min_length=2, max_length=30)
    product_price: float = Field(gt=0, le=1000000)
    product_rating: float | None = Field(ge=1, le=5, default=None)
    product_photo_path: str


class UpdateCatalogResponseModel(BaseModel):
    products: List[ProductCatalogCardModel]
