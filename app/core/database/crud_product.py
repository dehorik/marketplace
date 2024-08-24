from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class ProductDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с товарами"""

    def __init__(self, session: Session):
        self.__session = session
        self._cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__session.commit()
        self._cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(
            self,
            product_owner_id: int,
            product_name: str,
            product_price: float,
            product_description: str,
            product_photo_path: str
    ) -> list:
        self._cursor.execute(
            """
                INSERT INTO product (
                    product_owner_id, 
                    product_name, 
                    product_price, 
                    product_description, 
                    product_photo_path
                )
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING *;
            """,
            [
                product_owner_id,
                product_name,
                product_price,
                product_description,
                product_photo_path
            ]
        )

        return self._cursor.fetchall()

    def read(self, product_id: int) -> list:
        self._cursor.execute(
            """
                SELECT * 
                FROM product
                WHERE product_id = %s;
            """,
            [product_id]
        )

        return self._cursor.fetchall()

    def update(
            self,
            product_id: int,
            product_name: str,
            product_price: float,
            product_description: str,
            product_photo_path: str
    ) -> list:
        self._cursor.execute(
            """
                UPDATE product
                SET
                    product_name = %s,
                    product_price = %s,
                    product_description = %s,
                    product_photo_path = %s
                WHERE product_id = %s
                RETURNING *;
            """,
            [product_name, product_price, product_description, product_photo_path, product_id]
        )

        return self._cursor.fetchall()

    def delete(self, product_id: int) -> list:
        self._cursor.execute(
            """
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *;
            """,
            [product_id]
        )

        return self._cursor.fetchall()

    def get_catalog(self, amount: int, last_product_id: int | None = None) -> list:
        """
        Для получения последних созданных товаров и последующей подгрузки их в каталог

        :param amount: количество возвращаемых товаров
        :param last_product_id: product_id последнего товара из предыдущей подгрузки;
               если это первый запрос на получение последних товаров в каталог, то ничего не предавать
        :return: список товаров
        """

        if last_product_id:
            self._cursor.execute(
                """
                    SELECT product_id, product_name, product_price, product_photo_path
                    FROM product
                    WHERE product_id < %s
                    ORDER BY product_id DESC
                    LIMIT %s;
                """,
                [last_product_id, amount]
            )

            return self._cursor.fetchall()

        else:
            self._cursor.execute(
                """
                    SELECT product_id, product_name, product_price, product_photo_path
                    FROM product
                    ORDER BY product_id DESC
                    LIMIT %s;
                """,
                [amount]
            )

            return self._cursor.fetchall()
