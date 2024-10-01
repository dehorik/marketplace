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
            product_name: str,
            product_price: float,
            product_description: str,
            product_photo_path: str
    ) -> list:
        self._cursor.execute(
            """
                INSERT INTO product (
                    product_name, 
                    product_price, 
                    product_description, 
                    product_photo_path
                )
                VALUES
                    (%s, %s, %s, %s)
                RETURNING *
            """,
            [
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
                    product_name,
                    product_price, 
                    product_description,
                    is_hidden,
                    product_photo_path,
                    (
                        SELECT 
                            ROUND(AVG(comment_rating), 1) as product_rating
                        FROM 
                            product INNER JOIN comment 
                            ON product.product_id = comment.product_id
                        WHERE product.product_id = %s
                    ) AS product_rating,
                    (
                        SELECT COUNT(comment_id)
                        FROM comment 
                        WHERE product_id = %s
                    ) AS amount_comments
                FROM product
                WHERE product_id = %s;
            """,
            [product_id] * 3
        )

        return self._cursor.fetchall()

    def update(self, product_id: int, **kwargs) -> list:
        if not kwargs:
            self._cursor.execute(
                """
                    SELECT *
                    FROM product 
                    WHERE product_id = %s;
                """,
                [product_id]
            )

            return self._cursor.fetchall()

        set_values = ""
        for key, value in kwargs.items():
            if type(value) is str:
                set_values = set_values + f"{key} = '{value}', "
            else:
                set_values = set_values + f"{key} = {value}, "
        else:
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

    def delete(self, product_id: int) -> dict:
        deleted_items = {
            "product": None,
            "comments": [],
            "shopping_bag_items": []
        }

        self._cursor.execute(
            """
                DELETE 
                FROM comment
                WHERE product_id = %s
                RETURNING *;
            """,
            [product_id]
        )
        deleted_items['comments'].extend(self._cursor.fetchall())

        self._cursor.execute(
            """
                DELETE 
                FROM shopping_bag_item
                WHERE product_id = %s
                RETURNING *; 
            """,
            [product_id]
        )
        deleted_items["shopping_bag_items"].extend(self._cursor.fetchall())

        self._cursor.execute(
            """
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *; 
            """,
            [product_id]
        )
        deleted_items['product'] = self._cursor.fetchone()

        return deleted_items

    def get_catalog(
            self,
            amount: int = 9,
            last_product_id: int | None = None
    ) -> list:
        if last_product_id:
            condition = f"""
                WHERE product.product_id < {last_product_id} 
                AND product.is_hidden != true
            """
        else:
            condition = "WHERE product.is_hidden != true"

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
                            ROUND(AVG(comment_rating), 1) as product_rating
                        FROM 
                            product INNER JOIN comment 
                            ON product.product_id = comment.product_id
                        GROUP BY product.product_id
                    ) AS rating
                    ON product.product_id = rating.product_id
                {condition}
                ORDER BY product.product_id DESC
                LIMIT {amount};
            """
        )

        return self._cursor.fetchall()

    def search_product(
            self,
            product_name: str,
            amount: int = 9,
            last_product_id: int = None
    ) -> list:
        if last_product_id:
            condition = f"""
                WHERE LOWER(product.product_name) LIKE '%{product_name.lower()}%'
                AND product.product_id < {last_product_id}
                AND product.is_hidden != true
            """
        else:
            condition = f"""
                WHERE LOWER(product.product_name) LIKE '%{product_name.lower()}%'
                AND product.is_hidden != true
            """

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
                            ROUND(AVG(comment_rating), 1) as product_rating
                        FROM 
                            product INNER JOIN comment 
                            ON product.product_id = comment.product_id
                        GROUP BY product.product_id
                    ) AS rating
                    ON product.product_id = rating.product_id                
                {condition}
                ORDER BY product.product_id DESC
                LIMIT {amount};
            """
        )

        return self._cursor.fetchall()
