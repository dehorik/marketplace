from uuid import uuid4
from fastapi import UploadFile

from utils.converters import ProductConverter
from core.models.poduct import ProductModel
from core.database.crud_product import DataBaseProduct
from core.database.session_factory import BaseSession, ConnectorData
from core.config_reader import config


class ProductCreater:
    def __call__(
        self,
        product_owner_id: int,
        product_name: str,
        product_price: float,
        product_description: str,
        product_photo: UploadFile
    ):
        product_photo_path = f'database_data/product_photo/{uuid4()}'
        relative_path = '../' + product_photo_path
        with open(relative_path, 'wb') as photo:
            photo.write(product_photo.file.read())

        connector_data = ConnectorData(config)
        session = BaseSession(connector_data)
        cursor = session.get_cursor()
        db = DataBaseProduct(cursor)
        new_obj = db.create(
            product_owner_id,
            product_name,
            product_price,
            product_description,
            product_photo_path
        )

        converter = ProductConverter(ProductModel)
        model = converter.serialization(new_obj)[0]

        return model

