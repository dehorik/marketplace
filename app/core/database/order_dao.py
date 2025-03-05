from datetime import date

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class OrderDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с заказами"""

    def __init__(self, session: Session):
        self.__session = session

    def __execute(
            self,
            query: str,
            params: list | None = None,
            fetchone: bool = False
    ) -> list | tuple:
        """
        :param query: sql запрос
        :param params: параметры для подстановки в запрос
        :param fetchone: если True, возвращает одну строку; если False — все строки
               (для запросов, которые не возвращают данные, параметр игнорируется)
        """

        try:
            cursor = self.__session.get_cursor()
            cursor.execute(query, params)

            if cursor.description:
                return cursor.fetchone() if fetchone else cursor.fetchall()
            else:
                return []
        finally:
            cursor.close()

    def create(
            self,
            user_id: int,
            product_id: int,
            date_start: date,
            date_end: date,
            delivery_address: str
    ) -> tuple:
        return self.__execute(
            query="""
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
                RETURNING *;  
            """,
            params=[
                user_id,
                product_id,
                product_id,
                product_id,
                date_start,
                date_end,
                delivery_address,
            ],
            fetchone=True
        )

    def read(
            self,
            user_id: int,
            amount: int = 15,
            last_id: int | None = None
    ) -> list:
        query_parts = ["""
            SELECT 
                orders.order_id,
                orders.user_id,
                orders.product_id,
                orders.product_name,
                orders.product_price,
                orders.date_start,
                orders.date_end,
                orders.delivery_address,
                orders.has_photo
            FROM 
                product INNER JOIN orders
                ON product.product_id = orders.product_id
        """]
        params = []

        if last_id:
            query_parts.append("""
                WHERE orders.user_id = %s AND orders.order_id < %s
                ORDER BY orders.order_id DESC
                LIMIT %s;
            """)
            params.extend([user_id, last_id, amount])
        else:
            query_parts.append("""
                WHERE orders.user_id = %s 
                ORDER BY orders.order_id DESC
                LIMIT %s;
            """)
            params.extend([user_id, amount])

        return self.__execute(query="".join(query_parts), params=params)

    def update(
            self,
            order_id: int,
            user_id: int,
            date_end: date,
            delivery_address: str
    ) -> tuple:
        return self.__execute(
            query="""
                UPDATE orders
                SET date_end = %s, delivery_address = %s
                WHERE order_id = %s AND user_id = %s
                RETURNING *;
            """,
            params=[date_end, delivery_address, order_id, user_id],
            fetchone=True
        )

    def delete(self, order_id: int, user_id: int) -> tuple:
        order = self.__execute(
            query="""
                DELETE 
                FROM orders
                WHERE order_id = %s AND user_id = %s
                RETURNING *;
            """,
            params=[order_id, user_id],
            fetchone=True
        )

        if order:
            self.__execute(
                query="""
                    INSERT INTO archived_orders (user_id, product_id)
                    VALUES (%s, %s);
                """,
                params=[order[1], order[2]]
            )

        return order

    def delete_undefined_orders(self) -> list:
        # удаление всех заказов, у которых product_id или user_id равны null;
        # null появляется вместо внешнего ключа,
        # если связанная запись была удалена

        return self.__execute(
            query="""
                DELETE 
                FROM orders
                WHERE product_id IS NULL OR user_id IS NULL
                RETURNING *;
            """
        )

    def get_order_notification_data(self, order_id: int) -> tuple:
        return self.__execute(
            query="""
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
            params=[order_id],
            fetchone=True
        )


def get_order_dao() -> OrderDataAccessObject:
    session = get_session()
    return OrderDataAccessObject(session)
