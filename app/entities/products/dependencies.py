from typing import Annotated
from fastapi import Form, UploadFile, HTTPException, status

from core.config_reader import config
from core.database import ProductDataBase, CommentDataBase
from utils import Converter, FileWriter, FileReWriter, FileDeleter
from entities.products.models import ProductModel, ProductCatalogCardModel


class UpdateCatalog:
    def __init__(self, amount: int, last_product_id: int | None = None):
        converter = Converter(ProductCatalogCardModel)

        with ProductDataBase() as product_db:
            products = product_db.get_catalog(amount, last_product_id)
            self.products = converter.serialization(products)


class CreateProduct:
    def __init__(
            self,
            user_id: int,
            product_name: Annotated[str, Form(min_length=2, max_length=30)],
            product_price: Annotated[float, Form(gt=0, le=1000000)],
            product_description: Annotated[str, Form(min_length=2, max_length=300)],
            product_photo: UploadFile
    ):
        if not product_photo.content_type.split('/')[0] == 'image':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        converter = Converter(ProductModel)

        with ProductDataBase() as product_db:
            product_photo_path = FileWriter(
                config.getenv("PRODUCT_PHOTO_PATH"),
                product_photo.file.read()
            ).path

            product = product_db.create(
                user_id,
                product_name,
                product_price,
                product_description,
                product_photo_path
            )

            self.product = converter.serialization(product)[0]


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
                    detail='invalid file type'
                )

        converter = Converter(ProductModel)

        with ProductDataBase() as product_db:
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
                product_photo_path = product[0][-1]
                FileReWriter(product_photo_path, product_photo.file.read())

            self.product = converter.serialization(product)[0]


class DeleteProduct:
    def __init__(self, product_id: int):
        converter = Converter(ProductModel)

        with CommentDataBase() as comment_db:
            comments = comment_db.read(product_id)

            for comment in comments:
                deleted_comment = comment_db.delete(comment[0])
                deleted_comment_photo_path = deleted_comment[0][-1]

                if deleted_comment_photo_path:
                    FileDeleter(deleted_comment_photo_path)

        with ProductDataBase() as product_db:
            product = product_db.delete(product_id)

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='incorrect product_id'
                )

            deleted_product_photo_path = product[0][-1]
            FileDeleter(deleted_product_photo_path)

            self.product = converter.serialization(product)[0]
