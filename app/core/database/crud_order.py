from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class OrderDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с заказами"""

    def __init__(self, session: Session = Session()):
        self.__session = session
        self._cursor = session.get_cursor()

    def __del__(self):
        self.close()

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

    def get_orders_by_product_id(self, product_id: int) -> list:
        self._cursor.execute(
            """
                SELECT 
                    orders.order_id,
                    orders.product_id,
                    orders.user_id,
                    orders.order_date_start,
                    orders.order_date_end,
                    orders.order_address
                FROM 
                    orders INNER JOIN product 
                    ON orders.product_id = product.product_id
                WHERE orders.product_id = %s;
            """,
            [product_id]
        )

        return self._cursor.fetchall()

    def add_to_shopping_bag(self, product_id: int, user_id: int) -> list:
        self._cursor.execute(
            """
                INSERT INTO shopping_bag_item (
                    product_id,
                    user_id
                )
                VALUES (
                    %s, %s
                )
                RETURNING *;
            """,
            [product_id, user_id]
        )

        return self._cursor.fetchall()

    def delete_from_shopping_bag(self, shopping_bag_item_id: int) -> list:
        self._cursor.execute(
            """
                DELETE 
                FROM shopping_bag_item
                WHERE shopping_bag_item_id = %s
                RETURNING *;   
            """,
            [shopping_bag_item_id]
        )

        return self._cursor.fetchall()
