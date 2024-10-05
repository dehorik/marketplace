from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class OrderDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с заказами и товарами в корзине"""

    def __init__(self, session: Session = Session()):
        self.__session = session
        self._cursor = session.get_cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self.__session.commit()
        self._cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def get_all_orders(self, product_id: int) -> list:
        """Получить все заказы определенного товара"""

        self._cursor.execute(
            """
                SELECT 
                    orders.order_id,
                    orders.product_id,
                    orders.user_id,
                    orders.date_start,
                    orders.date_end,
                    orders.delivery_address
                FROM 
                    orders INNER JOIN product 
                    ON orders.product_id = product.product_id
                WHERE orders.product_id = %s;
            """,
            [product_id]
        )

        return self._cursor.fetchall()

    def add_to_cart(self, user_id: int, product_id: int) -> list:
        self._cursor.execute(
            """
                INSERT INTO cart_item (
                    product_id,
                    user_id
                )
                VALUES (%s, %s)
                RETURNING *;
            """,
            [product_id, user_id]
        )

        return self._cursor.fetchall()

    def delete_from_cart(self, user_id: int, cart_item_id: int) -> list:
        self._cursor.execute(
            """
                DELETE 
                FROM cart_item
                WHERE cart_item_id = %s AND user_id = %s
                RETURNING *;   
            """,
            [cart_item_id, user_id]
        )

        return self._cursor.fetchall()

    def get_cart(
            self,
            user_id: int,
            amount: int = 10,
            last_item_id: int | None = None
    ) -> list:
        if last_item_id:
            condition = f"""
                WHERE cart_item.user_id = {user_id} 
                AND cart_item.cart_item_id < {last_item_id}
            """
        else:
            condition = f"WHERE cart.user_id = {user_id}"

        self._cursor.execute(
            f"""
                SELECT
                    cart_item.cart_item_id,
                    cart_item.user_id,
                    cart_item.product_id,
                    cart_item.product_name,
                    cart_item.product_price
                FROM 
                    cart_item INNER JOIN product
                    ON cart_item.product_id = product.product_id
                {condition}
                ORDER BY cart_item.cart_item_id DESC
                LIMIT {amount};
            """
        )

        return self._cursor.fetchall()
