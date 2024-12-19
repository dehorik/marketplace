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
            name: str,
            price: float,
            description: str,
            is_hidden: bool
    ) -> tuple:
        self.__cursor.execute(
            """
                INSERT INTO product (
                    name, 
                    price, 
                    description,
                    is_hidden
                )
                VALUES
                    (%s, %s, %s, %s)
                RETURNING product_id;
            """,
            [name, price, description, is_hidden]
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

        return self.__cursor.fetchone()

    def read(self, product_id: int, user_id: int | None = None) -> tuple:
        self.__cursor.execute(
            """
                SELECT 
                    product_id,
                    name,
                    price, 
                    description,
                    is_hidden,
                    (
                        SELECT EXISTS (
                            SELECT 1
                            FROM cart_item
                            WHERE product_id = %s AND user_id = %s
                        )
                    ) as is_in_cart,
                    amount_orders,
                    photo_path,
                    (
                        SELECT 
                            CASE
                                WHEN COUNT(*) = 0 THEN 0.0
                                ELSE ROUND(SUM(rating)::DECIMAL / COUNT(*), 1)
                            END AS rating
                        FROM comment 
                        WHERE product_id = %s
                    ) AS rating,
                    (
                        SELECT COUNT(*)
                        FROM comment 
                        WHERE product_id = %s
                    ) AS amount_comments
                FROM product
                WHERE product_id = %s;
            """,
            [product_id, user_id, product_id, product_id, product_id]
        )

        return self.__cursor.fetchone()

    def update(
            self,
            product_id: int,
            name: str | None = None,
            price: int | None = None,
            description: str | None = None,
            is_hidden: bool | None = None
    ) -> tuple:
        fields = {
            key: value
            for key, value in {
                "name": name,
                "price": price,
                "description": description,
                "is_hidden": is_hidden
            }.items()
            if value is not None
        }

        if not fields:
            self.__cursor.execute(
                """
                    SELECT *
                    FROM product 
                    WHERE product_id = %s;
                """,
                [product_id]
            )

            return self.__cursor.fetchone()

        set_values = ""
        for key, value in fields.items():
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

        return self.__cursor.fetchone()

    def delete(self, product_id: int) -> tuple:
        self.__cursor.execute(
            """
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *; 
            """,
            [product_id]
        )

        return self.__cursor.fetchone()

    def get_latest_products(
            self,
            amount: int = 9,
            last_id: int | None = None
    ) -> list:
        condition = """
            WHERE product.is_hidden != true
        """

        if last_id:
            condition += f"AND product.product_id < {last_id}"

        self.__cursor.execute(
            f"""
                SELECT 
                    product.product_id, 
                    product.name, 
                    product.price, 
                    COALESCE(rating.rating, 0),
                    COALESCE(rating.amount_comments, 0),
                    product.photo_path
                FROM 
                    product LEFT JOIN (
                        SELECT 
                            product.product_id,
                            ROUND(AVG(comment.rating), 1) as rating,
                            COUNT(comment_id) as amount_comments
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
            name: str,
            amount: int = 9,
            last_id: int | None = None
    ) -> list:
        condition = f"""
            WHERE LOWER(product.name) LIKE '%{name.lower()}%'
            AND product.is_hidden != true
        """

        if last_id:
            condition += f"AND product.product_id < {last_id}"

        self.__cursor.execute(
            f"""
                SELECT 
                    product.product_id,
                    product.name,
                    product.price,
                    COALESCE(rating.rating, 0),
                    COALESCE(rating.amount_comments, 0),
                    product.photo_path
                FROM 
                    product LEFT JOIN (
                        SELECT 
                            product.product_id,
                            ROUND(AVG(comment.rating), 1) as rating,
                            COUNT(comment_id) as amount_comments
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
