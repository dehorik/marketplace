from os.path import join
from typing import Annotated
from fastapi import UploadFile, File, Form, Query, Path, Cookie
from fastapi import BackgroundTasks, Depends, HTTPException, status

from entities.products.models import (
    ProductModel,
    ExtendedProductModel,
    ProductCardModel,
    ProductCardListModel
)
from auth import admin_dependency, TokenPayloadModel
from core.tasks import comments_removal_task, orders_removal_task
from core.database import ProductDataAccessObject, get_product_dao
from utils import Converter, FileWriter, FileRemover


class ProductCreationService:
    """Создание товара"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject,
            converter: Converter,
            file_writer: FileWriter
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter
        self.file_writer = file_writer

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(admin_dependency)],
            name: Annotated[str, Form(min_length=5, max_length=30)],
            price: Annotated[int, Form(gt=0, le=100000)],
            description: Annotated[str, Form(min_length=150, max_length=300)],
            photo: Annotated[UploadFile, File()]
    ) -> ProductModel:
        if not check_file(photo):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail='invalid file type'
            )

        product = self.product_data_access_obj.create(name, price, description)
        product = self.converter.fetchone(product)

        self.file_writer(product.product_id, photo.file.read())

        return product


class FetchProductsService:
    """Получение последних созданных товаров"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject,
            converter: Converter
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(
            self,
            amount: Annotated[int, Query(ge=0)] = 15,
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
    """Поиск товара"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject,
            converter: Converter
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(
            self,
            name: Annotated[str, Query()],
            amount: Annotated[int, Query(ge=0)] = 15,
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


class FetchProductService:
    """Получение товара"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject,
            converter: Converter
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter

    def __call__(
            self,
            product_id: Annotated[int, Path(ge=1)],
            user_id: Annotated[str | None, Cookie()] = None
    ) -> ExtendedProductModel:
        try:
            product = self.product_data_access_obj.read(product_id, user_id)
            product = self.converter.fetchone(product)

            return product
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )


class ProductUpdateService:
    """Обновление данных товара"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject,
            converter: Converter,
            file_writer: FileWriter
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter
        self.file_writer = file_writer

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(admin_dependency)],
            product_id: Annotated[int, Path(ge=1)],
            name: Annotated[str, Form(min_length=5, max_length=30)] = None,
            price: Annotated[int, Form(gt=0, le=100000)] = None,
            description: Annotated[str, Form(min_length=150, max_length=300)] = None,
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
                description=description,
            )
            product = self.converter.fetchone(product)

            if photo:
                self.file_writer(product.product_id, photo.file.read())

            return product
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )


class ProductDeletionService:
    """Удаление товара"""

    def __init__(
            self,
            product_dao: ProductDataAccessObject,
            converter: Converter,
            file_remover: FileRemover
    ):
        self.product_data_access_obj = product_dao
        self.converter = converter
        self.file_remover = file_remover

    def __call__(
            self,
            background_tasks: BackgroundTasks,
            payload: Annotated[TokenPayloadModel, Depends(admin_dependency)],
            product_id: Annotated[int, Path(ge=1)]
    ) -> ProductModel:
        try:
            product = self.product_data_access_obj.delete(product_id)
            product = self.converter.fetchone(product)

            background_tasks.add_task(comments_removal_task)
            background_tasks.add_task(orders_removal_task)

            self.file_remover(product.product_id)

            return product
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='product not found'
            )


def check_file(file: UploadFile) -> bool:
    return file.content_type.split('/')[0] == 'image'


product_creation_service = ProductCreationService(
    product_dao=get_product_dao(),
    converter=Converter(ProductModel),
    file_writer=FileWriter(join("images", "products"))
)

fetch_products_service = FetchProductsService(
    product_dao=get_product_dao(),
    converter=Converter(ProductCardModel)
)

product_search_service = ProductSearchService(
    product_dao=get_product_dao(),
    converter=Converter(ProductCardModel)
)

fetch_product_service = FetchProductService(
    product_dao=get_product_dao(),
    converter=Converter(ExtendedProductModel)
)

product_update_service = ProductUpdateService(
    product_dao=get_product_dao(),
    converter=Converter(ProductModel),
    file_writer=FileWriter(join("images", "products"))
)

product_deletion_service = ProductDeletionService(
    product_dao=get_product_dao(),
    converter=Converter(ProductModel),
    file_remover=FileRemover(join("images", "products"))
)
