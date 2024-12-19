from typing import Annotated
from fastapi import HTTPException, Depends, Query, Path, status
from psycopg2.errors import ForeignKeyViolation, RaiseException

from entities.cart_items.models import (
    CartItemCreationRequest,
    CartItemModel,
    CartItemCardModel,
    CartItemCardListModel
)
from auth import AuthorizationService, TokenPayloadModel
from core.database import CartItemDataAccessObject, get_cart_item_dao
from utils import Converter


user_dependency = AuthorizationService(min_role_id=1)
admin_dependency = AuthorizationService(min_role_id=2)
superuser_dependency = AuthorizationService(min_role_id=3)


class CartItemCreationService:
    """Добавление товара в корзину"""

    def __init__(
            self,
            cart_item_dao: CartItemDataAccessObject = get_cart_item_dao(),
            converter: Converter = Converter(CartItemModel)
    ):
        self.cart_item_data_access_obj = cart_item_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            data: CartItemCreationRequest
    ) -> CartItemModel:
        try:
            cart_item = self.cart_item_data_access_obj.create(
                payload.sub,
                data.product_id
            )
            cart_item = self.converter.fetchone(cart_item)

            return cart_item
        except RaiseException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="product not found"
            )
        except ForeignKeyViolation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found"
            )


class CartItemLoadService:
    """Загрузка карточек товаров в корзине"""

    def __init__(
            self,
            cart_item_dao: CartItemDataAccessObject = get_cart_item_dao(),
            converter: Converter = Converter(CartItemCardModel)
    ):
        self.cart_item_data_access_obj = cart_item_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            amount: Annotated[int, Query(ge=0)] = 10,
            last_id: Annotated[int | None, Query(ge=1)] = None
    ) -> CartItemCardListModel:
        """
        :param amount: требуемое количество карточек
        :param last_id: id карточки товара в корзине
               из последней подгрузки (если это первый запрос - None)
        """

        cart_items = self.cart_item_data_access_obj.read(
            user_id=payload.sub,
            amount=amount,
            last_id=last_id
        )
        cart_items = self.converter.fetchmany(cart_items)

        return CartItemCardListModel(cart_items=cart_items)


class CartItemRemovalService:
    """Удаление товара из корзины"""

    def __init__(
            self,
            cart_item_dao: CartItemDataAccessObject = get_cart_item_dao(),
            converter: Converter = Converter(CartItemModel)
    ):
        self.cart_item_data_access_obj = cart_item_dao
        self.converter = converter

    def __call__(
            self,
            payload: Annotated[TokenPayloadModel, Depends(user_dependency)],
            cart_item_id: Annotated[int, Path(ge=1)]
    ) -> CartItemModel:
        try:
            cart_item = self.cart_item_data_access_obj.delete(
                cart_item_id,
                payload.sub
            )
            cart_item = self.converter.fetchone(cart_item)

            return cart_item
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="cart item not found"
            )


cart_item_creation_service = CartItemCreationService()
cart_item_load_service = CartItemLoadService()
cart_item_removal_service = CartItemRemovalService()
