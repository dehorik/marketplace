from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, status

from core.database import Session, ProductDataBase
from core.models.poduct import ProductModel
from utils.converters import ProductConverter
from utils.uuid_generator import IDGenerator


product_router = APIRouter(
    prefix='/products',
    tags=['prodcuts']
)


@product_router.post('/create')
def create_product(
        product_owner_id: Annotated[int, Form()],
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo: UploadFile
):
    product_photo_path = f'database_data/product_photo/{IDGenerator()()}'
    relative_path = '../' + product_photo_path
    with open(relative_path, 'wb') as photo:
        photo.write(product_photo.file.read())

    session = Session()
    db = ProductDataBase(session)
    new_obj = db.create(
        product_owner_id,
        product_name,
        product_price,
        product_description,
        product_photo_path
    )

    converter = ProductConverter(ProductModel)
    model = converter.serialization(new_obj)[0]

    session.commit()

    return {
        'status': status.HTTP_201_CREATED,
        'object': model
    }

