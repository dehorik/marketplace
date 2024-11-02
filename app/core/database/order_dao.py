import os
from datetime import datetime
from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject
from core.settings import config


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
    ) -> tuple:
        self.__cursor.execute(
            """
                INSERT INTO orders (
                    user_id,
                    product_id,
                    product_name,
                    product_price,
                    date_start,
                    date_end,
                    delivery_address
                )
                VALUES (
                    %s, %s, 
                    (SELECT name FROM product WHERE product_id = %s),
                    (SELECT price FROM product WHERE product_id = %s),
                    NOW(),
                    %s, %s 
                )
                RETURNING order_id;
            """,
            [
                user_id,
                product_id,
                product_id,
                product_id,
                date_end,
                delivery_address,
            ]
        )

        order_id = self.__cursor.fetchone()[0]
        photo_path = os.path.join(config.ORDER_CONTENT_PATH, str(order_id))

        self.__cursor.execute(
            """
                UPDATE orders
                SET photo_path = %s
                WHERE order_id = %s
                RETURNING *;
            """,
            [photo_path, order_id]
        )

        return self.__cursor.fetchone()

    def read(
            self,
            user_id: int,
            amount: int = 10,
            last_id: int | None = None
    ) -> list:
        condition = f"""
            WHERE orders.user_id = {user_id}
        """

        if last_id:
            condition += f"AND orders.order_id < {last_id}"

        self.__cursor.execute(
            f"""
                SELECT 
                    orders.order_id,
                    orders.user_id,
                    product.product_id,
                    orders.product_name,
                    orders.product_price,
                    orders.date_start,
                    orders.date_end,
                    orders.delivery_address,
                    orders.photo_path,
                    product.is_hidden
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

    def delete(self, order_id: int) -> tuple:
        self.__cursor.execute(
            """
                DELETE 
                FROM orders
                WHERE order_id = %s
                RETURNING *;
            """
        )

        return self.__cursor.fetchone()

    def get_order_notification_data(self, order_id: int) -> tuple:
        self.__cursor.execute(
            """
                SELECT 
                    orders.order_id,
                    orders.product_name,
                    orders.product_price,
                    orders.date_start,
                    orders.date_end,
                    orders.delivery_address,
                    users.username,
                    users.email
                FROM
                    orders INNER JOIN users
                    ON orders.user_id = users.user_id
                WHERE order_id = %s;
            """,
            [order_id]
        )

        return self.__cursor.fetchone()

    def craete_cart_item(self, user_id: int, product_id: int) -> tuple:
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

    def get_cart_items(
            self,
            user_id: int,
            amount: int = 10,
            last_id: int | None = None
    ) -> list:
        condition = f"""
            WHERE cart_item.user_id = {user_id}
            AND product.is_hidden = false
        """

        if last_id:
            condition += f"AND cart_item.cart_item_id < {last_id}"

        self.__cursor.execute(
            f"""
                SELECT
                    cart_item.cart_item_id,
                    cart_item.user_id,
                    cart_item.product_id,
                    product.name,
                    product.price
                FROM 
                    cart_item INNER JOIN product
                    ON cart_item.product_id = product.product_id
                {condition}
                ORDER BY cart_item.cart_item_id DESC
                LIMIT {amount};
            """
        )

        return self.__cursor.fetchall()

    def delete_cart_item(self, cart_item_id: int, user_id: int) -> tuple:
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


def get_order_dao() -> OrderDataAccessObject:
    session = get_session()
    return OrderDataAccessObject(session)
