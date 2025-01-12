from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class CartItemDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с товарами в корзине"""

    def __init__(self, session: Session):
        self.__session = session

    def create(self, user_id: int, product_id: int) -> tuple:
        cursor = self.__session.get_cursor()
        cursor.execute(
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
        data = cursor.fetchone()
        cursor.close()

        return data

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
                product.price,
                product.photo_path
            FROM 
                cart_item INNER JOIN product USING(product_id)     
        """
        params = []

        if last_id:
            query += """
                WHERE cart_item.user_id = %s AND cart_item.cart_item_id < %s
                ORDER BY cart_item.cart_item_id DESC
                LIMIT %s;
            """
            params.extend([user_id, last_id, amount])
        else:
            query += """
                WHERE cart_item.user_id = %s
                ORDER BY cart_item.cart_item_id DESC
                LIMIT %s;
            """
            params.extend([user_id, amount])

        cursor = self.__session.get_cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()

        return data

    def update(self):
        raise NotImplementedError("update is not supported for cart items")

    def delete(self, cart_item_id: int, user_id: int) -> tuple:
        cursor = self.__session.get_cursor()
        cursor.execute(
            """
                DELETE 
                FROM cart_item
                WHERE cart_item_id = %s AND user_id = %s
                RETURNING *;   
            """,
            [cart_item_id, user_id]
        )
        data = cursor.fetchone()
        cursor.close()

        return data


def get_cart_item_dao() -> CartItemDataAccessObject:
    session = get_session()
    return CartItemDataAccessObject(session)
