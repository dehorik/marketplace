from typing import Annotated
from fastapi import Form, UploadFile, HTTPException, status

from core import Session, ProductDataBase, CommentDataBase
from utils import Converter, FileWriter, FileReWriter, FileDeleter
from entities.products.models import ProductModel, ProductCatalogCardModel


class UpdateCatalog:
    def __init__(self, amount: int, last_product_id: int | None = None):
        converter = Converter(ProductCatalogCardModel)
        session = Session()
        product_db = ProductDataBase(session)

        products = product_db.get_catalog(amount, last_product_id)

        product_db.close()
        self.products = converter.serialization(products)


class CreateProduct:
    def __init__(
            self,
            product_owner_id: int,
            product_name: Annotated[str, Form(min_length=2, max_length=30)],
            product_price: Annotated[float, Form(gt=0, le=1000000)],
            product_description: Annotated[str, Form(min_length=2, max_length=300)],
            product_photo: UploadFile
    ):
        if not product_photo.content_type.split('/')[0] == 'image':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='incorrect product_photo file type!'
            )

        file_writer = FileWriter()
        converter = Converter(ProductModel)
        session = Session()
        product_db = ProductDataBase(session)

        product_photo_path = file_writer(FileWriter.product_path, product_photo.file.read())
        new_product = product_db.create(
            product_owner_id,
            product_name,
            product_price,
            product_description,
            product_photo_path
        )

        product_db.close()
        self.product = converter.serialization(new_product)[0]


class UpdateProduct:
    def __init__(
            self,
            product_id: int,
            product_name: Annotated[str | None, Form(min_length=2, max_length=30)] = None,
            product_price: Annotated[float | None, Form(gt=0, le=1000000)] = None,
            product_description: Annotated[str | None, Form(min_length=2, max_length=300)] = None,
            product_photo: UploadFile | None = None
    ):
        if product_photo:
            if not product_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='incorrect product_photo file type!'
                )

        converter = Converter(ProductModel)
        session = Session()
        product_db = ProductDataBase(session)

        params = {
            'product_name': product_name,
            'product_price': product_price,
            'product_description': product_description
        }
        params = {key: value for key, value in params.items() if value is not None}
        product = product_db.update(product_id, **params)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect product_id'
            )

        if product_photo:
            file_rewriter = FileReWriter()
            file_rewriter(product[0][-1], product_photo.file.read())

        product_db.close()
        self.product = converter.serialization(product)[0]


class DeleteProduct:
    def __init__(self, product_id: int):
        file_deleter = FileDeleter()
        converter = Converter(ProductModel)
        session = Session()
        product_db = ProductDataBase(session)
        comment_db = CommentDataBase(session)

        comments = comment_db.read(product_id)
        for comment in comments:
            deleted_comment = comment_db.delete(comment[0])
            deleted_comment_photo_path = deleted_comment[0][-1]

            if deleted_comment_photo_path:
                file_deleter(deleted_comment_photo_path)

        product = product_db.delete(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect product_id'
            )

        deleted_product_path = product[0][-1]
        file_deleter(deleted_product_path)

        product_db.close()
        comment_db.close()
        self.product = converter.serialization(product)[0]

