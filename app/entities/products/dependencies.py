from typing import Annotated
from fastapi import Form, UploadFile, HTTPException, status

from core.config_reader import config
from core.database import ProductDataBase, CommentDataBase
from utils import Converter, FileWriter, FileReWriter, FileDeleter
from entities.products.models import ProductModel, ProductCatalogCardModel


class BaseDependency:
    """
    Базовый класс для других классов-зависимостей,
    предоставляющий объектам дочерних классов ссылки на экземпляры
    FileWriter, ProductDataBase и т.д.
    """

    def __init__(
            self,
            file_writer: Annotated[type, FileWriter] = FileWriter,
            file_rewriter: Annotated[type, FileReWriter] = FileReWriter,
            file_deleter: Annotated[type, FileDeleter] = FileDeleter,
            producct_database: Annotated[type, ProductDataBase] = ProductDataBase,
            comment_database: Annotated[type, CommentDataBase] = CommentDataBase
    ):
        """
        :param file_writer: ссылка на класс для записи файлов
        :param file_rewriter: ссылка на класс для перезаписи файлов
        :param file_deleter: ссылка на класс для удаления файлов
        :param producct_database: ссылка на класс для работы с БД (товар)
        :param comment_database: ссылка на класс для работы с БД (отзывы)
        """

        self.file_writer = file_writer
        self.file_rewriter = file_rewriter
        self.file_deleter = file_deleter
        self.product_database = producct_database
        self.comment_database = comment_database


class Catalog(BaseDependency):
    def __init__(
            self,
            converter: Converter = Converter(ProductCatalogCardModel)
    ):
        super().__init__()
        self.converter = converter

    def __call__(self) -> list:
        with self.product_database() as product_db:
            products = product_db.get_catalog(amount=9)
            return self.converter.serialization(products)


class UpdateCatalog(BaseDependency):
    def __init__(
            self,
            converter: Converter = Converter(ProductCatalogCardModel)
    ):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            amount: int,
            last_product_id: int | None = None
    ) -> list:
        with self.product_database() as product_db:
            products = product_db.get_catalog(amount, last_product_id)
            return self.converter.serialization(products)


class CreateProduct(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            user_id: int,
            product_name: Annotated[str, Form(min_length=2, max_length=30)],
            product_price: Annotated[float, Form(gt=0, le=1000000)],
            product_description: Annotated[str, Form(min_length=2, max_length=300)],
            product_photo: UploadFile
    ) -> ProductModel:
        if not product_photo.content_type.split('/')[0] == 'image':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        with self.product_database() as product_db:
            product_photo_path = self.file_writer(
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

            return self.converter.serialization(product)[0]


class UpdateProduct(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: int,
            product_name: Annotated[str | None, Form(min_length=2, max_length=30)] = None,
            product_price: Annotated[float | None, Form(gt=0, le=1000000)] = None,
            product_description: Annotated[str | None, Form(min_length=2, max_length=300)] = None,
            product_photo: UploadFile | None = None
    ) -> ProductModel:
        if product_photo:
            if not product_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        with self.product_database() as product_db:
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
                self.file_rewriter(product_photo_path, product_photo.file.read())

            return self.converter.serialization(product)[0]


class DeleteProduct(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, product_id: int) -> ProductModel:
        with self.comment_database() as comment_db:
            comments = comment_db.read(product_id)

            for comment in comments:
                deleted_comment = comment_db.delete(comment[0])
                deleted_comment_photo_path = deleted_comment[0][-1]

                if deleted_comment_photo_path:
                    self.file_deleter(deleted_comment_photo_path)

        with self.product_database() as product_db:
            product = product_db.delete(product_id)

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='incorrect product_id'
                )

            deleted_product_photo_path = product[0][-1]
            self.file_deleter(deleted_product_photo_path)

            return self.converter.serialization(product)[0]
