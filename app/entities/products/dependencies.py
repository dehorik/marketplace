from typing import Annotated, Callable
from fastapi import UploadFile, File, Form, Query, Path
from fastapi import BackgroundTasks, Depends, HTTPException, status
from psycopg2.errors import RaiseException

from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardModel,
    ProductCardListModel
)
from auth import AuthorizationService, TokenPayloadModel
from core.tasks import comments_removal_task
from core.database import ProductDataAccessObject, get_product_dao
from utils import Converter, write_file, delete_file


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class ProductCreationService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductModel),
            file_writer: Callable = write_file
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter
        self.file_writer = file_writer

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(admin_dependency)],
            name: Annotated[str, Form(min_length=2, max_length=20)],
            price: Annotated[int, Form(gt=0, le=100000)],
            description: Annotated[str, Form(min_length=2, max_length=300)],
            is_hidden: Annotated[bool, Form()],
            photo: Annotated[UploadFile, File()]
    ) -> ProductModel:
        if not check_file(photo):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        product = self.product_data_access_obj.create(
            name,
            price,
            description,
            is_hidden
        )
        product = self.converter.fetchone(product)

        background_tasks.add_task(
            self.file_writer,
            product.photo_path, photo.file.read()
        )

        return product


class CatalogLoadService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductCardModel)
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(
            self,
            amount: Annotated[int, Query(ge=0)] = 9,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> ProductCardListModel:
        """
        :param amount: количество возвращаемых товаров
        :param last_id: id последнего товара из предыдущей подгрузки;
               при первом запросе ничего не передавать
        """

        products = self.product_data_access_obj.get_latest_products(
            amount=amount,
            last_id=last_id
        )
        products = self.converter.fetchmany(products)

        return ProductCardListModel(products=products)


class ProductSearchService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductCardModel)
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(
            self,
            name: Annotated[str, Query(min_length=2, max_length=20)],
            amount: Annotated[int, Query(ge=0)] = 9,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> ProductCardListModel:
        """
        :param name: имя товара
        :param amount: максимальное количество товаров в ответе
        :param last_id: id товара из последней подгрузки
        """

        products = self.product_data_access_obj.search_product(
            name=name,
            amount=amount,
            last_id=last_id
        )
        products = self.converter.fetchmany(products)

        return ProductCardListModel(products=products)


class ProductFetchService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ExtendedProductModel)
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(self, product_id: int) -> ExtendedProductModel:
        try:
            product = self.product_data_access_obj.read(product_id)
            product = self.converter.fetchone(product)

            return product
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )


class ProductUpdateService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductModel),
            file_writer: Callable = write_file
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter
        self.file_writer = file_writer

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(admin_dependency)],
            product_id: Annotated[int, Path(ge=1)],
            name: Annotated[str | None, Form(min_length=2, max_length=30)] = None,
            price: Annotated[int | None, Form(gt=0, le=100000)] = None,
            descr: Annotated[str | None, Form(min_length=2, max_length=300)] = None,
            is_hidden: Annotated[bool | None, Form()] = None,
            photo: Annotated[UploadFile, File()] = None
    ) -> ProductModel:
        if photo:
            if not check_file(photo):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail='invalid file type'
                )

        try:
            product = self.product_data_access_obj.update(
                product_id=product_id,
                name=name,
                price=price,
                description=descr,
                is_hidden=is_hidden
            )
            product = self.converter.fetchone(product)

            if photo:
                background_tasks.add_task(
                    self.file_writer,
                    product.photo_path, photo.file.read()
                )

            return product
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )


class ProductRemovalService:
    def __init__(
            self,
            product_dao: ProductDataAccessObject = get_product_dao(),
            converter: Converter = Converter(ProductModel),
            file_delter: Callable = delete_file
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter
        self.file_delter = file_delter

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(admin_dependency)],
            product_id: Annotated[int, Path(ge=1)]
    ) -> ProductModel:
        try:
            product = self.product_data_access_obj.delete(product_id)
            product = self.converter.fetchone(product)

            background_tasks.add_task(
                self.file_delter,
                product.photo_path
            )
            background_tasks.add_task(comments_removal_task)

            return product
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="there are orders with this product"
            )


def check_file(file: UploadFile) -> bool:
    return file.content_type.split('/')[0] == 'image'


product_creation_service = ProductCreationService()
product_fetch_service = ProductFetchService()
product_update_service = ProductUpdateService()
product_removal_service = ProductRemovalService()
catalog_load_service = CatalogLoadService()
product_search_service = ProductSearchService()
