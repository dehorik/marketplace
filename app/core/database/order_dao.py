from datetime import datetime
from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class OrderDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с заказами и товарами в корзине"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(
            self,
            user_id: int,
            product_id: int,
            date_end: datetime,
            delivery_address: str
    ) -> list:
        self.__cursor.execute(
            """
                INSERT INTO orders (
                    user_id,
                    product_id,
                    date_start,
                    date_end,
                    delivery_address
                )
                VALUES (%s, %s, CURRENT_DATE, %s, %s)
                RETURNING *;
            """,
            [user_id, product_id, date_end, delivery_address]
        )

        return self.__cursor.fetchall()

    def read(
            self,
            user_id: int,
            amount: int = 10,
            last_order_id: int | None = None
    ) -> list:
        condition = f"WHERE orders.user_id = {user_id}"

        if last_order_id:
            condition += f"AND orders.order_id < {last_order_id}"

        self.__cursor.execute(
            f"""
                SELECT 
                    orders.order_id,
                    product.product_id,
                    orders.user_id,
                    orders.date_start,
                    orders.date_end,
                    orders.delivery_address,
                    product.product_name,
                    product.product_price,
                    product.is_hidden,
                    product.photo_path
                FROM 
                    product INNER JOIN orders
                    ON product.product_id = orders.product_id
                {condition}
                ORDER BY orders.date_start DESC
                LIMIT {amount};
            """
        )

        return self.__cursor.fetchall()

    def update(self):
        pass

    def delete(self, order_id: int) -> list:
        self.__cursor.execute(
            """
                DELETE 
                FROM orders
                WHERE order_id = %s
                RETURNING *;
            """
        )

        return self.__cursor.fetchall()

    def get_order_letter_data(self, order_id: int) -> list:
        self.__cursor.execute(
            """
                SELECT 
                    orders.order_id,
                    orders.date_start,
                    orders.date_end,
                    orders.delivery_address,
                    users.username,
                    users.email,
                    product.product_name,
                    product.product_price
                FROM product
                    INNER JOIN orders USING(product_id)
                    INNER JOIN users USING(user_id)
                WHERE order_id = %s;
            """,
            [order_id]
        )

        return self.__cursor.fetchall()

    def get_all_orders(self, product_id: int) -> list:
        """Получить все заказы определенного товара"""

        self.__cursor.execute(
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

        return self.__cursor.fetchall()

    def add_to_cart(self, user_id: int, product_id: int) -> list:
        self.__cursor.execute(
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

        return self.__cursor.fetchall()

    def delete_from_cart(self, user_id: int, cart_item_id: int) -> list:
        self.__cursor.execute(
            """
                DELETE 
                FROM cart_item
                WHERE cart_item_id = %s AND user_id = %s
                RETURNING *;   
            """,
            [cart_item_id, user_id]
        )

        return self.__cursor.fetchall()

    def get_cart(
            self,
            user_id: int,
            amount: int = 10,
            last_item_id: int | None = None
    ) -> list:
        condition = f"""
            WHERE cart_item.user_id = {user_id}
            AND product.is_hidden = false
        """

        if last_item_id:
            condition += f"AND cart_item.cart_item_id < {last_item_id}"

        self.__cursor.execute(
            f"""
                SELECT
                    cart_item.cart_item_id,
                    cart_item.user_id,
                    cart_item.product_id,
                    product.product_name,
                    product.product_price
                FROM 
                    cart_item INNER JOIN product
                    ON cart_item.product_id = product.product_id
                {condition}
                ORDER BY cart_item.cart_item_id DESC
                LIMIT {amount};
            """
        )

        return self.__cursor.fetchall()


def get_order_dao() -> OrderDataAccessObject:
    session = get_session()
    return OrderDataAccessObject(session)
