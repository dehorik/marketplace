from typing import Annotated
from fastapi import Form, UploadFile

from core import Session, ProductDataBase
from entities.products.models import ProductModel
from utils import Converter, FileWriter, FileReWriter, FileDeleter


class CreateProduct:
    def __init__(
            self,
            product_owner_id: Annotated[int, Form()],
            product_name: Annotated[str, Form(min_length=2, max_length=30)],
            product_price: Annotated[float, Form(gt=0, le=1000000)],
            product_description: Annotated[str, Form(min_length=2, max_length=300)],
            product_photo: UploadFile
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
        db.close()

        self.product = converter.serialization(new_product)[0]


class UpdateCatalog:
    def __init__(self, amount: int, last_product_id: int):
        converter = Converter(ProductModel)
        session = Session()
        db = ProductDataBase(session)

        products = db.get_catalog(amount, last_product_id)
        db.close()

        self.products = converter.serialization(products)


class UpdateProduct:
    def __init__(
            self,
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
        db.close()

        self.product = converter.serialization(product)[0]


class DeleteProduct:
    def __init__(self, product_id: int):
        file_deleter = FileDeleter()
        session = Session()
        db = ProductDataBase(session)

        product = db.delete(product_id)[0]
        db.close()
        deleted_product_path = product[-1]
        file_deleter(deleted_product_path)

        self.product = product

