import os

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject
from core.settings import config


class ProductDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с товарами"""

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
            product_name: str,
            product_price: float,
            product_description: str,
            is_hidden: bool
    ) -> list:
        self.__cursor.execute(
            """
                INSERT INTO product (
                    product_name, 
                    product_price, 
                    product_description,
                    is_hidden
                )
                VALUES
                    (%s, %s, %s, %s)
                RETURNING product_id;
            """,
            [product_name, product_price, product_description, is_hidden]
        )

        product_id = self.__cursor.fetchone()[0]
        photo_path = os.path.join(config.PRODUCT_CONTENT_PATH, str(product_id))

        self.__cursor.execute(
            """                 
                UPDATE product
                SET photo_path = %s
                WHERE product_id = %s
                RETURNING *;
            """,
            [photo_path, product_id]
        )

        return self.__cursor.fetchall()

    def read(self, product_id: int) -> list:
        self.__cursor.execute(
            """
                SELECT 
                    product_id,
                    product_name,
                    product_price, 
                    product_description,
                    is_hidden,
                    amount_orders,
                    photo_path,
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

        return self.__cursor.fetchall()

    def update(self, product_id: int, **kwargs) -> list:
        if not kwargs:
            self.__cursor.execute(
                """
                    SELECT *
                    FROM product 
                    WHERE product_id = %s;
                """,
                [product_id]
            )

            return self.__cursor.fetchall()

        set_values = ""
        for key, value in kwargs.items():
            if type(value) is str:
                set_values += f"{key} = '{value}', "
            else:
                set_values += f"{key} = {value}, "
        else:
            set_values = set_values[:-2]

        self.__cursor.execute(
            f"""
                UPDATE product 
                SET {set_values}                
                WHERE product_id = {product_id}
                RETURNING *;
            """
        )

        return self.__cursor.fetchall()

    def delete(self, product_id: int) -> list:
        self.__cursor.execute(
            """
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *; 
            """,
            [product_id]
        )

        return self.__cursor.fetchall()

    def get_latest_products(
            self,
            amount: int = 9,
            last_product_id: int | None = None
    ) -> list:
        condition = "WHERE product.is_hidden != true"

        if last_product_id:
            condition += f"AND product.product_id < {last_product_id}"

        self.__cursor.execute(
            f"""
                SELECT 
                    product.product_id, 
                    product.product_name, 
                    product.product_price, 
                    rating.product_rating,
                    product.photo_path
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

        return self.__cursor.fetchall()

    def search_product(
            self,
            product_name: str,
            amount: int = 9,
            last_product_id: int | None = None
    ) -> list:
        condition = f"""
            WHERE LOWER(product.product_name) LIKE '%{product_name.lower()}%'
            AND product.is_hidden != true
        """

        if last_product_id:
            condition += f"AND product.product_id < {last_product_id}"

        self.__cursor.execute(
            f"""
                SELECT 
                    product.product_id,
                    product.product_name,
                    product.product_price,
                    rating.product_rating,
                    product.photo_path
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

        return self.__cursor.fetchall()


def get_product_dao() -> ProductDataAccessObject:
    session = get_session()
    return ProductDataAccessObject(session)
