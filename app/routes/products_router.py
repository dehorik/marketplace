from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, status

from services.product_service import ProductCreater


router = APIRouter(
    prefix='/products'
)


@router.get('/load')
def load_products_to_page(step: int):
    pass


@router.post('/create')
def create_product(
        product_owner_id: Annotated[int, Form()],
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo: UploadFile
):
    service = ProductCreater()
    obj = service(product_owner_id, product_name, product_price, product_description, product_photo)

    return {
        'status': status.HTTP_201_CREATED,
        'object': obj
    }

