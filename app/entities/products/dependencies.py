from typing import Annotated, Type
from os.path import exists
from fastapi import Form, UploadFile, HTTPException, File, Query, status

from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardModel,
    ProductCardListModel
)
from utils import (
    FileWriter,
    FileRewriter,
    FileDeleter,
    PathGenerator,
    Converter
)
from core.settings import config
from core.database import ProductDataBase, OrderDataBase


class BaseDependency:
    """Базовый класс для других классов-зависимостей"""

    def __init__(
            self,
            file_writer: FileWriter = FileWriter(),
            file_rewriter: FileRewriter = FileRewriter(),
            file_deleter: FileDeleter = FileDeleter(),
            path_generator: PathGenerator = PathGenerator(config.PRODUCT_PHOTO_PATH),
            product_database: Type[ProductDataBase] = ProductDataBase,
            order_database: Type[OrderDataBase] = OrderDataBase
    ):
        """
        :param file_writer: ссылка на объект для записи файлов
        :param file_rewriter: ссылка на объект для перезаписи файлов
        :param file_deleter: ссылка на объект для удаления файлов
        :param path_generator: объект для генерации путей к изображениям
        :param product_database: ссылка на класс для работы с БД (товары)
        :param order_database: ссылка на класс для работы с БД (заказы)
        """

        self.file_writer = file_writer
        self.file_rewriter = file_rewriter
        self.file_deleter = file_deleter
        self.path_generator = path_generator
        self.product_database = product_database
        self.order_database = order_database


class CatalogLoader(BaseDependency):
    """Получение последних созданных товаров"""

    def __init__(self, converter: Converter = Converter(ProductCardModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            amount: Annotated[int, Query(ge=0)] = 9,
            last_product_id: Annotated[int | None, Query(ge=1)] = None
    ) -> ProductCardListModel:
        """
        :param amount: количество возвращаемых товаров
        :param last_product_id: product_id последнего товара
               из предыдущей подгрузки;
               при первом запросе оставить None

        :return: список товаров
        """

        with self.product_database() as product_db:
            products = product_db.get_catalog(
                amount=amount,
                last_product_id=last_product_id
            )

        return ProductCardListModel(
            products=self.converter.serialization(products)
        )


class ProductSearcher(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductCardModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_name: Annotated[str, Query(min_length=2, max_length=20)],
            amount: Annotated[int, Query(ge=0)] = 9,
            last_product_id: Annotated[int | None, Query(ge=1)] = None
    ) -> ProductCardListModel:
        """
        :param product_name: имя товара
        :param amount: максимальное количество товаров в ответе
        :param last_product_id: id товара из последней подгрузки

        :return: список найденных товаров
        """

        with self.product_database() as product_db:
            products = product_db.search_product(
                product_name=product_name,
                amount=amount,
                last_product_id=last_product_id
            )

        return ProductCardListModel(
            products=self.converter.serialization(products)
        )


class ProductCreator(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_name: Annotated[
                str, Form(min_length=2, max_length=20)
            ],
            product_price: Annotated[
                int, Form(gt=0, le=1000000)
            ],
            product_description: Annotated[
                str, Form(min_length=2, max_length=300)
            ],
            is_hidden: Annotated[
                bool, Form()
            ],
            product_photo: Annotated[
                UploadFile, File()
            ]
    ) -> ProductModel:
        if not product_photo.content_type.split('/')[0] == 'image':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        with self.product_database() as product_db:
            product = product_db.create(
                product_name,
                product_price,
                product_description,
                is_hidden
            )

            product = product_db.update(
                product_id=product[0][0],
                product_photo_path=self.path_generator(product[0][0])
            )

        product = self.converter.serialization(product)[0]

        self.file_writer(
            product.product_photo_path,
            product_photo.file.read()
        )

        return product


class ProductGetter(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
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

        product[0] = list(product[0])
        product_rating = product[0].pop(-2)
        amount_comments = product[0].pop(-1)

        return ExtendedProductModel(
            product_data=self.converter.serialization(product)[0],
            product_rating=product_rating,
            amount_comments=amount_comments
        )


class ProductUpdater(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_id: int,
            product_name: Annotated[
                str | None, Form(min_length=2, max_length=30)
            ] = None,
            product_price: Annotated[
                int | None, Form(gt=0, le=1000000)
            ] = None,
            product_description: Annotated[
                str | None, Form(min_length=2, max_length=300)
            ] = None,
            is_hidden: Annotated[
                bool | None, Form()
            ] = None,
            product_photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> ProductModel:
        if product_photo:
            if not product_photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            product_photo_path = self.path_generator(product_id)

            if exists(product_photo_path):
                self.file_rewriter(
                    product_photo_path,
                    product_photo.file.read()
                )

        fields_for_update = {
            key: value
            for key, value in {
                'product_name': product_name,
                'product_price': product_price,
                'product_description': product_description,
                'is_hidden': is_hidden
            }.items()
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

        return self.converter.serialization(product)[0]


class ProductDeleter(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(self, product_id: int) -> ProductModel:
        with self.order_database() as order_db:
            if order_db.get_orders_by_product_id(product_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="there are orders with this product"
                )

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
load_catalog_dependency = CatalogLoader()
search_product_dependency = ProductSearcher()
create_product_dependency = ProductCreator()
get_product_dependency = ProductGetter()
update_product_dependency = ProductUpdater()
delete_product_dependency = ProductDeleter()
