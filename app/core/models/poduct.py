from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: int
    product_owner_id: int
    product_name: str = Field(min_length=2, max_length=30)
    product_price: float = Field(gt=0, le=1000000)
    product_description: str = Field(max_length=300)
    product_photo: str
