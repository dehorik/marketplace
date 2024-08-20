from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, status

from services.product_service import ProductCreater, LastProductLoader


router = APIRouter(
    prefix='/products'
)


@router.get('/load')
def load_last_products(step: int):
    service = LastProductLoader()
    models = service(step)

    return {
        'status': status.HTTP_200_OK,
        'objects': models
    }


@router.post('/create')
def create_product(
        product_owner_id: Annotated[int, Form()],
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo: UploadFile
):
    service = ProductCreater()
    model = service(product_owner_id, product_name, product_price, product_description, product_photo)

    return {
        'status': status.HTTP_201_CREATED,
        'object': model
    }

