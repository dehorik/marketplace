import os
from typing import Annotated, Callable
from fastapi import (
    BackgroundTasks, HTTPException, Query, UploadFile, File, Form, status
)

from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardModel,
    ProductCardListModel
)
from auth import AuthorizationService
from core.tasks import product_removal_task
from core.database import (
    ProductDataAccessObject,
    OrderDataAccessObject,
    get_product_dao,
    get_order_dao
)
from core.settings import config
from utils import Converter, exists, write_file, delete_file


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class CatalogLoaderService:
    """Получение последних созданных товаров"""

    def __init__(
            self,
            file_writer: Callable = write_file,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductCardModel)
    ):
        self.file_writer = file_writer
        self.product_data_access_obj = product_dao
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

        products = self.product_data_access_obj.get_latest_products(
            amount=amount,
            last_product_id=last_product_id
        )

        return ProductCardListModel(
            products=self.converter(products)
        )


class ProductSearchService:
    """Поиск товара по названию"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductCardModel)
    ):
        self.product_data_access_obj = product_dao
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

        products = self.product_data_access_obj.search_product(
            product_name=product_name,
            amount=amount,
            last_product_id=last_product_id
        )

        return ProductCardListModel(
            products=self.converter(products)
        )


class ProductCreationService:
    def __init__(
            self,
            file_writer: Callable = write_file,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductModel)
    ):
        self.file_writer = file_writer
        self.product_data_access_obj = product_dao
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
            photo: Annotated[
                UploadFile, File()
            ]
    ) -> ProductModel:
        if not photo.content_type.split('/')[0] == 'image':
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        product = self.product_data_access_obj.create(
            product_name,
            product_price,
            product_description,
            is_hidden
        )
        product = self.converter(product)[0]
        self.file_writer(product.photo_path, photo.file.read())

        return product


class ProductFetchService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductModel)
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(self, product_id: int) -> ExtendedProductModel:
        product = self.product_data_access_obj.read(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )

        product[0] = list(product[0])
        product_rating = product[0].pop(-2)
        amount_comments = product[0].pop(-1)

        return ExtendedProductModel(
            product_data=self.converter(product)[0],
            product_rating=product_rating,
            amount_comments=amount_comments
        )


class ProductUpdateService:
    def __init__(
            self,
            file_writer: Callable = write_file,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductModel)
    ):
        self.file_writer = file_writer
        self.product_data_access_obj = product_dao
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

            photo_path = os.path.join(
                config.PRODUCT_CONTENT_PATH,
                str(product_id)
            )

            if exists(photo_path):
                self.file_writer(photo_path, photo.file.read())

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

        product = self.product_data_access_obj.update(
            product_id=product_id,
            **fields_for_update
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )

        return self.converter(product)[0]


class ProductRemovalService:
    def __init__(
            self,
            file_deleter: Callable = delete_file,
            product_dao: ProductDataAccessObject = get_product_dao(),
            order_dao: OrderDataAccessObject = get_order_dao(),
            converter: Converter = Converter(ProductModel)
    ):
        self.file_deleter = file_deleter
        self.product_data_access_obj = product_dao
        self.order_data_access_obj = order_dao
        self.converter = converter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            product_id: int
    ) -> ProductModel:
        if self.order_data_access_obj.get_all_orders(product_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="there are orders with this product"
            )

        product = self.product_data_access_obj.delete(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )

        background_tasks.add_task(product_removal_task)
        product = self.converter(product)[0]
        self.file_deleter(product.photo_path)

        return product


# dependencies
catalog_loader_service = CatalogLoaderService()
product_search_service = ProductSearchService()
product_creation_service = ProductCreationService()
product_fetch_service = ProductFetchService()
product_update_service = ProductUpdateService()
product_removal_service = ProductRemovalService()
