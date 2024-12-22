import os
from datetime import date

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject
from core.settings import config


class OrderDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с заказами"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__cursor.close()

    def create(
            self,
            user_id: int,
            product_id: int,
            date_start: date,
            date_end: date,
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
                    %s, %s, %s 
                )
                RETURNING order_id;
            """,
            [
                user_id,
                product_id,
                product_id,
                product_id,
                date_start,
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
        query = """
            SELECT 
                orders.order_id,
                orders.user_id,
                orders.product_id,
                orders.product_name,
                orders.product_price,
                product.is_hidden,
                orders.date_start,
                orders.date_end,
                orders.delivery_address,
                orders.photo_path
            FROM 
                product INNER JOIN orders
                ON product.product_id = orders.product_id
        """
        params = []

        if last_id:
            query += """
                WHERE orders.user_id = %s AND orders.order_id < %s
                ORDER BY orders.order_id DESC
                LIMIT %s;
            """
            params.extend([user_id, last_id, amount])
        else:
            query += """
                WHERE orders.user_id = %s 
                ORDER BY orders.order_id DESC
                LIMIT %s;
            """
            params.extend([user_id, amount])

        self.__cursor.execute(query, params)

        return self.__cursor.fetchall()

    def update(
            self,
            order_id: int,
            user_id: int,
            date_end: date,
            delivery_address: str
    ) -> tuple:
        self.__cursor.execute(
            """
                UPDATE orders
                SET 
                    date_end = %s,
                    delivery_address = %s
                WHERE order_id = %s AND user_id = %s
                RETURNING *;
            """,
            [date_end, delivery_address, order_id, user_id]
        )

        return self.__cursor.fetchone()

    def delete(self, order_id: int, user_id: int) -> tuple:
        self.__cursor.execute(
            """
                DELETE 
                FROM orders
                WHERE order_id = %s AND user_id = %s
                RETURNING *;
            """,
            [order_id, user_id]
        )

        return self.__cursor.fetchone()

    def delete_undefined_orders(self) -> list:
        self.__cursor.execute(
            """
                DELETE 
                FROM orders
                WHERE product_id IS NULL OR user_id IS NULL
                RETURNING *;
            """
        )

        return self.__cursor.fetchall()

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


def get_order_dao() -> OrderDataAccessObject:
    session = get_session()
    return OrderDataAccessObject(session)
