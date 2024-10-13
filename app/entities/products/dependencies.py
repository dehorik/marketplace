from os.path import exists
from typing import Annotated, Type, Callable
from fastapi import Form, UploadFile, HTTPException, File, Query, status

from entities.comments.models import CommentModel
from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardModel,
    ProductCardListModel
)
from auth import PayloadTokenModel, AuthorizationService
from core.settings import config
from core.database import ProductDAO, CommentDAO, OrderDAO
from utils import Converter, write_file, delete_file


base_user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
owner_dependency = AuthorizationService(min_role_id=3)


class BaseDependency:
    def __init__(
            self,
            file_writer: Callable = write_file,
            file_deleter: Callable = delete_file,
            product_database: Type[ProductDAO] = ProductDAO,
            comment_database: Type[CommentDAO] = CommentDAO,
            order_database: Type[OrderDAO] = OrderDAO
    ):
        """
        :param file_writer: ссылка на объект для записи и перезаписи файлов
        :param file_deleter: ссылка на объект для удаления файлов
        :param product_database: ссылка на класс для работы с БД (товары)
        :param comment_database: ссылка на класс для работы с БД (отзывы)
        :param order_database: ссылка на класс для работы с БД (заказы)
        """

        self.file_writer = file_writer
        self.file_deleter = file_deleter
        self.product_database = product_database
        self.comment_database = comment_database
        self.order_database = order_database


class CatalogLoaderService(BaseDependency):
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
               из предыдущей подгрузки; первый запрос - оставить None
        """

        with self.product_database() as product_db:
            products = product_db.get_catalog(
                amount=amount,
                last_product_id=last_product_id
            )

        return ProductCardListModel(
            products=self.converter(products)
        )


class ProductSearchService(BaseDependency):
    """Поиск товара по названию"""

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
        """

        with self.product_database() as product_db:
            products = product_db.search_product(
                product_name=product_name,
                amount=amount,
                last_product_id=last_product_id
            )

        return ProductCardListModel(
            products=self.converter(products)
        )


class ProductCreationService(BaseDependency):
    def __init__(self, converter: Converter = Converter(ProductModel)):
        super().__init__()
        self.converter = converter

    def __call__(
            self,
            product_name: Annotated[str, Form(min_length=2, max_length=20)],
            product_price: Annotated[int, Form(gt=0, le=1000000)],
            product_description: Annotated[str, Form(min_length=2, max_length=300)],
            is_hidden: Annotated[bool, Form()],
            photo: Annotated[UploadFile, File()]
    ) -> ProductModel:
        if not photo.content_type.split('/')[0] == 'image':
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

        product = self.converter(product)[0]
        self.file_writer(product.photo_path, photo.file.read())

        return product


class ProductGettingService(BaseDependency):
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
            product_data=self.converter(product)[0],
            product_rating=product_rating,
            amount_comments=amount_comments
        )


class ProductUpdateService(BaseDependency):
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
            photo: Annotated[
                UploadFile, File()
            ] = None
    ) -> ProductModel:
        if photo:
            if not photo.content_type.split('/')[0] == 'image':
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

            photo_path = f"{config.PRODUCT_CONTENT_PATH}/{product_id}"

            if exists(f"../{photo_path}"):
                self.file_writer(
                    photo_path,
                    photo.file.read()
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

        return self.converter(product)[0]


class ProductRemovalService(BaseDependency):
    def __init__(
            self,
            product_converter: Converter = Converter(ProductModel),
            comment_converter: Converter = Converter(CommentModel)
    ):
        super().__init__()
        self.product_converter = product_converter
        self.comment_converter = comment_converter

    def __call__(self, product_id: int) -> ProductModel:
        with self.order_database() as order_db:
            if order_db.get_all_orders(product_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="there are orders with this product"
                )

        with self.comment_database() as comment_db:
            comments = comment_db.delete_all_comments(product_id)

        for comment in self.comment_converter(comments):
            if comment.photo_path:
                self.file_deleter(comment.photo_path)

        with self.product_database() as product_db:
            product = product_db.delete(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="incorrect product_id"
            )

        product = self.product_converter(product)[0]
        self.file_deleter(product.photo_path)

        return product


# dependencies
catalog_loader_service = CatalogLoaderService()
product_search_service = ProductSearchService()
product_creation_service = ProductCreationService()
product_getting_service = ProductGettingService()
product_update_service = ProductUpdateService()
product_removal_service = ProductRemovalService()
