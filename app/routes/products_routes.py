from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, status

from core.database import Session, ProductDataBase
from core.models import ProductModel
from utils import FileWriter, ProductConverter


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
    converter = ProductConverter(ProductModel)
    writer = FileWriter(FileWriter.product)
    session = Session()
    db = ProductDataBase(session)

    product_photo_path = writer(product_photo.file.read())
    new_product = db.create(
        product_owner_id,
        product_name,
        product_price,
        product_description,
        product_photo_path
    )
    model = converter.serialization(new_product)[0]

    db.close()

    return {
        'status': status.HTTP_201_CREATED,
        'object': model
    }

