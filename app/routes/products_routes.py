from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, Request, status
from fastapi.responses import HTMLResponse

from core.database import Session, ProductDataBase
from core.models import ProductModel, UpdateCatalogResponseModel
from utils import FileWriter, FileDeleter, FileReWriter, Converter
from main import templates


router = APIRouter(
    prefix='/products',
    tags=['prodcuts']
)


@router.get("/{product_id}", response_class=HTMLResponse)
def get_product(product_id: int, request: Request):
    return templates.TemplateResponse(
        name='cart.html',
        request=request
    )

@router.post(
    '/create',
    response_model=ProductModel,
    status_code=status.HTTP_201_CREATED
)
def create_product(
        product_owner_id: Annotated[int, Form()],
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo: UploadFile,
):
    converter = Converter(ProductModel)
    file_writer = FileWriter()
    session = Session()
    db = ProductDataBase(session)

    product_photo_path = file_writer(FileWriter.product_path, product_photo.file.read())
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

@router.get("/update-catalog", response_model=UpdateCatalogResponseModel)
def update_catalog(amount: int, last_product_id: int):
    converter = Converter(ProductModel)
    session = Session()
    db = ProductDataBase(session)

    products = db.get_catalog(amount, last_product_id)
    models = converter.serialization(products)

    db.close()
    return {
        'products': models
    }

@router.put("/{product_id}", response_model=ProductModel)
def update_product(
        product_id: int,
        product_name: Annotated[str, Form(min_length=2, max_length=30)],
        product_price: Annotated[float, Form(gt=0, le=1000000)],
        product_description: Annotated[str, Form(min_length=2, max_length=300)],
        product_photo_path: str,
        product_photo: UploadFile | None = None
):
    converter = Converter(ProductModel)
    session = Session()
    db = ProductDataBase(session)

    if product_photo:
        file_rewriter = FileReWriter()
        file_rewriter(product_photo_path, product_photo.file.read())

    product = db.update(
        product_id,
        product_name,
        product_price,
        product_description,
        product_photo_path
    )
    model = converter.serialization(product)[0]

    db.close()
    return model

@router.delete("/{product_id}", response_model=ProductModel)
def delete_product(product_id: int):
    file_deleter = FileDeleter()
    session = Session()
    db = ProductDataBase(session)

    product = db.delete(product_id)[0]
    deleted_product_path = product[-1]
    file_deleter(deleted_product_path)

    db.close()
    return product
