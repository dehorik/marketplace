from typing import Annotated, Type, Callable
from fastapi import Form, UploadFile, HTTPException, File, status

from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCatalogCardModel,
    ProductCatalogModel
)
from core.settings import config
from core.database import ProductDataBase, CommentDataBase
from utils import Converter, write_file, rewrite_file, delete_file


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            file_writer: Callable = write_file,
            file_rewriter: Callable = rewrite_file,
            file_deleter: Callable = delete_file,
            producct_database: Type = ProductDataBase,
            comment_database: Type = CommentDataBase
    ):
        """
        :param file_writer: ссылка на функцию для записи файлов
        :param file_rewriter: ссылка на функцию для перезаписи файлов
        :param file_deleter: ссылка на функцию для удаления файлов
        :param producct_database: ссылка на класс для работы с БД (товар)
        :param comment_database: ссылка на класс для работы с БД (отзывы)
        """

        self.file_writer = file_writer
        self.file_rewriter = file_rewriter
        self.file_deleter = file_deleter
        self.product_database = producct_database
        self.comment_database = comment_database


class ProductCatalog(BaseDependency):
    def __init__(
            self,
            converter: Converter = Converter(ProductCatalogCardModel)
    ):
        super().__init__()
        self.converter = converter

    def __call__(self) -> ProductCatalogModel:
        with self.product_database() as product_db:
            products = product_db.get_catalog(amount=9)

            return ProductCatalogModel(
                products=self.converter.serialization(products)
            )


class CatalogLoader(BaseDependency):
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
    ) -> ProductCatalogModel:
        with self.product_database() as product_db:
            products = product_db.get_catalog(
                amount=amount,
                last_product_id=last_product_id
            )

            return ProductCatalogModel(
                products=self.converter.serialization(products)
            )


class ProductCreator(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_name: Annotated[
                str,
                Form(min_length=2, max_length=30)
            ],
            product_price: Annotated[
                int,
                Form(gt=0, le=1000000)
            ],
            product_description: Annotated[
                str,
                Form(min_length=2, max_length=300)
            ],
            product_photo: Annotated[
                UploadFile,
                File()
            ]
    ) -> ProductModel:
        if not product_photo.content_type.split('/')[0] == 'image':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        product_photo_path = self.file_writer(
            config.PRODUCT_PHOTO_PATH,
            product_photo.file.read()
        )

        with self.product_database() as product_db:
            product = product_db.create(
                product_name,
                product_price,
                product_description,
                product_photo_path
            )

        return self.converter.serialization(product)[0]


class ProductGetter(BaseDependency):
    def __init__(
            self,
            converter: Converter = Converter(ProductModel)
    ):
        super().__init__()
        self.converter = converter

    def __call__(self, product_id: int) -> ExtendedProductModel:
        with self.product_database() as product_db:
            product = product_db.read(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect product_id'
            )

        product = list(product[0])
        product_rating = product.pop(-1)

        return ExtendedProductModel(
            product=self.converter.serialization([product])[0],
            product_rating=product_rating
        )


class ProductUpdater(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: int,
            product_name: Annotated[
                str | None,
                Form(min_length=2, max_length=30)
            ] = None,
            product_price: Annotated[
                int | None,
                Form(gt=0, le=1000000)
            ] = None,
            product_description: Annotated[
                str | None,
                Form(min_length=2, max_length=300)
            ] = None,
            product_photo: Annotated[
                UploadFile,
                File()
            ] = None
    ) -> ProductModel:
        if product_photo:
            if not product_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        fields_for_update = {
            'product_name': product_name,
            'product_price': product_price,
            'product_description': product_description
        }
        fields_for_update = {
            key: value
            for key, value in fields_for_update.items()
            if value is not None
        }

        with self.product_database() as product_db:
            product = product_db.update(
                product_id=product_id,
                **fields_for_update
            )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='incorrect product_id'
            )

        product = self.converter.serialization(product)[0]

        if product_photo:
            self.file_rewriter(
                product.product_photo_path,
                product_photo.file.read()
            )

        return product


class ProductDeleter(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, product_id: int) -> ProductModel:
        with self.product_database() as product_db:
            deleted_items = product_db.delete(product_id)

        if not deleted_items['product']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )

        product = self.converter.serialization([deleted_items['product']])[0]
        self.file_deleter(product.product_photo_path)

        for comment in deleted_items['comments']:
            comment_photo_path = comment[-1]

            if comment_photo_path:
                self.file_deleter(comment_photo_path)

        return product


# dependencies
get_catalog_dependency = ProductCatalog()
load_catalog_dependency = CatalogLoader()
create_product_dependency = ProductCreator()
get_product_dependency = ProductGetter()
update_product_dependency = ProductUpdater()
delete_product_dependency = ProductDeleter()
