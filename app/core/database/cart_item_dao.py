from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class CartItemDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с товарами в корзине"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(self, user_id: int, product_id: int) -> tuple:
        self.__cursor.execute(
            """
                INSERT INTO cart_item (
                    user_id,
                    product_id
                )
                VALUES (%s, %s)
                RETURNING *;
            """,
            [user_id, product_id]
        )

        return self.__cursor.fetchone()

    def read(
            self,
            user_id: int,
            amount: int = 10,
            last_id: int | None = None
    ) -> list:
        query = """
            SELECT
                cart_item.cart_item_id,
                cart_item.user_id,
                cart_item.product_id,
                product.name,
                product.price
            FROM 
                cart_item INNER JOIN product
                ON cart_item.product_id = product.product_id
        """
        params = []

        if last_id:
            query += """
                WHERE cart_item.user_id = %s AND product.is_hidden = false AND cart_item.cart_item_id < %s
                ORDER BY cart_item.cart_item_id DESC
                LIMIT %s;
            """
            params.extend([user_id, last_id, amount])
        else:
            query += """
                WHERE cart_item.user_id = %s AND product.is_hidden = false 
                ORDER BY cart_item.cart_item_id DESC
                LIMIT %s;
            """
            params.extend([user_id, amount])

        self.__cursor.execute(query, params)

        return self.__cursor.fetchall()

    def update(self):
        raise NotImplementedError("update is not supported for cart items")

    def delete(self, cart_item_id: int, user_id: int) -> tuple:
        self.__cursor.execute(
            """
                DELETE 
                FROM cart_item
                WHERE cart_item_id = %s AND user_id = %s
                RETURNING *;   
            """,
            [cart_item_id, user_id]
        )

        return self.__cursor.fetchone()


def get_cart_item_dao() -> CartItemDataAccessObject:
    session = get_session()
    return CartItemDataAccessObject(session)
