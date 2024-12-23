from typing import List
from pydantic import BaseModel


class ProductModel(BaseModel):
    """Базовая схема товара"""

    product_id: int
    name: str
    price: int
    description: str
    is_hidden: bool
    amount_orders: int
    photo_path: str


class ExtendedProductModel(BaseModel):
    """Расширенная схема товара с дополнительными полями"""

    product_id: int
    name: str
    price: int
    description: str
    is_hidden: bool
    is_in_cart: bool
    rating: float
    amount_comments: int
    amount_orders: int
    photo_path: str


class ProductCardModel(BaseModel):
    """Схема карточки товара в каталоге"""

    product_id: int
    name: str
    price: int
    rating: float
    amount_comments: int
    photo_path: str


class ProductCardListModel(BaseModel):
    products: List[ProductCardModel]
