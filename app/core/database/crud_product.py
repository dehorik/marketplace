from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class ProductDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с товарами"""

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

    def create(
            self,
            user_id: int,
            product_name: str,
            product_price: float,
            product_description: str,
            product_photo_path: str
    ) -> list:
        self._cursor.execute(
            """
                INSERT INTO product (
                    user_id, 
                    product_name, 
                    product_price, 
                    product_description, 
                    product_photo_path
                )
                VALUES
                    (%s, %s, %s, %s, %s)
                RETURNING 
                    product_id,
                    user_id,
                    product_name,
                    product_price,
                    product_description,
                    NULL,
                    product_photo_path;
            """,
            [
                user_id,
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
                SELECT 
                    product_id,
                    user_id,
                    product_name,
                    product_price, 
                    product_description,
                    (
                        SELECT 
                            ROUND(AVG(comment_rating), 2) as product_rating
                        FROM 
                            product INNER JOIN comment 
                            ON product.product_id = comment.product_id
                        WHERE product.product_id = %s
                    ) AS rating,
                    product_photo_path 
                FROM product
                WHERE product_id = %s;
            """,
            [product_id, product_id]
        )

        return self._cursor.fetchall()

    def update(
            self,
            product_id: int,
            product_name: str | None = None,
            product_price: float | None = None,
            product_description: str | None = None
    ) -> list:
        params = {
            'product_name': product_name,
            'product_price': product_price,
            'product_description': product_description
        }
        params = {key: value for key, value in params.items() if value is not None}

        set_values = ""
        for key, value in params.items():
            if type(value) is str:
                set_values = set_values + f"{key} = '{value}', "
            else:
                set_values = set_values + f"{key} = {value}, "
        set_values = set_values[:-2]

        self._cursor.execute(
            f"""
                UPDATE product 
                    SET {set_values}                
                WHERE product_id = %s
                RETURNING *;
            """,
            [product_id]
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
            condition = f"WHERE product.product_id < {last_product_id}"
        else:
            condition = ""

        self._cursor.execute(
            f"""
                SELECT 
                    product.product_id, 
                    product.product_name, 
                    product.product_price, 
                    rating.product_rating,
                    product.product_photo_path
                FROM 
                    product LEFT JOIN (
                        SELECT 
                            product.product_id,
                            ROUND(AVG(comment_rating), 2) as product_rating
                        FROM 
                            product INNER JOIN comment 
                            ON product.product_id = comment.product_id
                        GROUP BY product.product_id
                    ) AS rating
                    ON product.product_id = rating.product_id
                {condition}
                ORDER BY product.product_id DESC
                LIMIT %s;
            """,
            [amount]
        )

        return self._cursor.fetchall()
