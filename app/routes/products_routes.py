from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, Request, status
from fastapi.responses import HTMLResponse

from core.database import Session, ProductDataBase
from core.models import ProductModel, UpdateCatalogResponseModel
from utils import FileWriter, Converter
from main import templates


product_router = APIRouter(
    prefix='/products',
    tags=['prodcuts']
)


@product_router.post(
    '/create',
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED
)
def create_product(
        product_owner_id: Annotated[int, Form()],
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo: UploadFile
):
    converter = Converter(ProductModel)
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
    return model

@product_router.get(
    "/update-catalog",
    response_model=UpdateCatalogResponseModel,
    status_code=status.HTTP_200_OK
)
def update_catalog(amount: int, last_product_id: int):
    converter = Converter(ProductModel)
    session = Session()
    db = ProductDataBase(session)

    products = db.update_catalog(amount, last_product_id)
    models = converter.serialization(products)

    db.close()
    return {
        'products': models
    }

@product_router.get("/{product_id}", response_class=HTMLResponse)
def get_product(product_id: int, request: Request):
    return templates.TemplateResponse(
        name='cart.html',
        request=request
    )

@product_router.put("/{product_id}", response_model=ProductModel)
def partly_update_product(
        product_id: int,
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo: UploadFile
):
    converter = Converter(ProductModel)
    writer = FileWriter(FileWriter.product)
    session = Session()
    db = ProductDataBase(session)

    product_photo_path = writer(product_photo.file.read())
    product = db.update(
        product_id,
        product_name=product_name,
        product_price=product_price,
        product_description=product_description,
        product_photo_path=product_photo_path
    )
    model = converter.serialization(product)[0]

    db.close()
    return model

@product_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    session = Session()
    db = ProductDataBase(session)

    db.delete(product_id)
    db.close()
