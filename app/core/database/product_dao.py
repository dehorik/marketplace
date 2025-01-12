import os

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject
from core.settings import config


class ProductDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с товарами"""

    def __init__(self, session: Session):
        self.__session = session

    def create(
            self,
            name: str,
            price: float,
            description: str,
    ) -> tuple:
        cursor = self.__session.get_cursor()
        cursor.execute(
            """
                INSERT INTO product (
                    name, 
                    price, 
                    description
                )
                VALUES
                    (%s, %s, %s)
                RETURNING product_id;
            """,
            [name, price, description]
        )

        data = cursor.fetchone()

        cursor.execute(
            """                 
                UPDATE product
                SET photo_path = %s
                WHERE product_id = %s
                RETURNING *;
            """,
            [
                os.path.join(config.PRODUCT_CONTENT_PATH, str(data[0])),
                data[0]
            ]
        )

        data = cursor.fetchone()
        cursor.close()

        return data

    def read(self, product_id: int, user_id: int | None = None) -> tuple:
        cursor = self.__session.get_cursor()
        cursor.execute(
            """
                SELECT 
                    product_id,
                    name,
                    price, 
                    description,
                    (
                        SELECT EXISTS (
                            SELECT order_id
                            FROM orders
                            WHERE user_id = %s AND product_id = %s
                            UNION
                            SELECT archived_order_id
                            FROM archived_orders
                            WHERE user_id = %s AND product_id = %s
                        )
                    ),
                    (
                        SELECT EXISTS (
                            SELECT 1
                            FROM cart_item
                            WHERE product_id = %s AND user_id = %s
                        )
                    ) AS is_in_cart,
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
                    ) AS amount_comments,
                    amount_orders,
                    photo_path
                FROM product
                WHERE product_id = %s;
            """,
            [
                user_id,
                product_id,
                user_id,
                product_id,
                product_id,
                user_id,
                product_id,
                product_id,
                product_id
            ]
        )
        data = cursor.fetchone()
        cursor.close()

        return data

    def update(
            self,
            product_id: int,
            name: str | None = None,
            price: int | None = None,
            description: str | None = None
    ) -> tuple:
        if not any([name, price, description]):
            cursor = self.__session.get_cursor()
            cursor.execute(
                """
                    SELECT *
                    FROM product 
                    WHERE product_id = %s;
                """,
                [product_id]
            )
            data = cursor.fetchone()
            cursor.close()

            return data

        query = """
            UPDATE product 
            SET   
        """
        params = []

        if name:
            query += " name = %s, "
            params.append(name)

        if price:
            query += " price = %s, "
            params.append(price)

        if description:
            query += " description = %s, "
            params.append(description)

        query = query[:-2] + """
            WHERE product_id = %s
            RETURNING *;
        """
        params.append(product_id)

        cursor = self.__session.get_cursor()
        cursor.execute(query, params)
        data = cursor.fetchone()
        cursor.close()

        return data

    def delete(self, product_id: int) -> tuple:
        cursor = self.__session.get_cursor()
        cursor.execute(
            """
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *; 
            """,
            [product_id]
        )
        data = cursor.fetchone()
        cursor.close()

        return data

    def get_latest_products(
            self,
            amount: int = 15,
            last_id: int | None = None
    ) -> list:
        query = """
            SELECT 
                product.product_id, 
                product.name, 
                product.price, 
                COALESCE(score.rating, 0),
                COALESCE(score.amount_comments, 0),
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
                ) AS score
                ON product.product_id = score.product_id
        """
        params = []

        if last_id:
            query += """
                WHERE product.product_id < %s
                ORDER BY product.product_id DESC
                LIMIT %s;
            """
            params.extend([last_id, amount])
        else:
            query += """
                ORDER BY product.product_id DESC
                LIMIT %s;
            """
            params.append(amount)

        cursor = self.__session.get_cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()

        return data

    def search_product(
            self,
            name: str,
            amount: int = 15,
            last_id: int | None = None
    ) -> list:
        query = """
            SELECT 
                product.product_id, 
                product.name, 
                product.price, 
                COALESCE(score.rating, 0),
                COALESCE(score.amount_comments, 0),
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
                ) AS score
                ON product.product_id = score.product_id
        """
        params = []

        if last_id:
            query += """
                WHERE LOWER(product.name) LIKE %s AND product.product_id < %s
                ORDER BY product.product_id DESC
                LIMIT %s;
            """
            params.extend([f"%{name.replace("%", "")}%", last_id, amount])
        else:
            query += """
                WHERE LOWER(product.name) LIKE %s 
                ORDER BY product.product_id DESC 
                LIMIT %s;
            """
            params.extend([f"%{name.replace("%", "")}%", amount])

        cursor = self.__session.get_cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()

        return data


def get_product_dao() -> ProductDataAccessObject:
    session = get_session()
    return ProductDataAccessObject(session)
