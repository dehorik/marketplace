from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class ProductDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с товарами"""

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
            name: str,
            price: float,
            description: str,
    ) -> tuple:
        return self.__execute(
            query="""
                INSERT INTO product (name, price, description)
                VALUES (%s, %s, %s)
                RETURNING *;
            """,
            params=[name, price, description],
            fetchone=True
        )

    def read(self, product_id: int, user_id: int | None = None) -> tuple:
        return self.__execute(
            query="""
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
                    ) AS is_ordered,
                    (
                        SELECT EXISTS (
                            SELECT cart_item_id
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
                    has_photo
                FROM product
                WHERE product_id = %s;
            """,
            params=[
                user_id,
                product_id,
                user_id,
                product_id,
                product_id,
                user_id,
                product_id,
                product_id,
                product_id
            ],
            fetchone=True
        )

    def update(
            self,
            product_id: int,
            name: str | None = None,
            price: int | None = None,
            description: str | None = None
    ) -> tuple:
        if not any([name, price, description]):
            return self.__execute(
                query="""
                    SELECT *
                    FROM product 
                    WHERE product_id = %s;
                """,
                params=[product_id],
                fetchone=True
            )

        fields = []
        params = []

        if name:
            fields.append("name = %s")
            params.append(name)

        if price:
            fields.append("price = %s")
            params.append(price)

        if description:
            fields.append("description = %s")
            params.append(description)

        query = f"""
            UPDATE product 
            SET {", ".join(fields)}
            WHERE product_id = %s
            RETURNING *;
        """
        params.append(product_id)

        return self.__execute(query=query, params=params, fetchone=True)

    def delete(self, product_id: int) -> tuple:
        return self.__execute(
            query="""
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *; 
            """,
            params=[product_id],
            fetchone=True
        )

    def get_latest_products(
            self,
            amount: int = 15,
            last_id: int | None = None
    ) -> list:
        query_parts = ["""
            SELECT 
                product.product_id, 
                product.name, 
                product.price, 
                COALESCE(score.rating, 0),
                COALESCE(score.amount_comments, 0),
                product.description,
                product.has_photo
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
        """]
        params = []

        if last_id:
            query_parts.append("""
                WHERE product.product_id < %s
                ORDER BY product.product_id DESC
                LIMIT %s;
            """)
            params.extend([last_id, amount])
        else:
            query_parts.append("""
                ORDER BY product.product_id DESC
                LIMIT %s;
            """)
            params.append(amount)

        return self.__execute(query="".join(query_parts), params=params)

    def search_product(
            self,
            name: str,
            amount: int = 15,
            last_id: int | None = None
    ) -> list:
        query_parts = ["""
            SELECT 
                product.product_id, 
                product.name, 
                product.price, 
                COALESCE(score.rating, 0),
                COALESCE(score.amount_comments, 0),
                product.description,
                product.has_photo
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
        """]
        params = []

        if last_id:
            query_parts.append("""
                WHERE LOWER(product.name) LIKE %s AND product.product_id < %s
                ORDER BY product.product_id DESC
                LIMIT %s;
            """)
            params.extend([f"%{name.replace("%", "")}%", last_id, amount])
        else:
            query_parts.append("""
                WHERE LOWER(product.name) LIKE %s 
                ORDER BY product.product_id DESC 
                LIMIT %s;
            """)
            params.extend([f"%{name.replace("%", "")}%", amount])

        return self.__execute(query="".join(query_parts), params=params)


def get_product_dao() -> ProductDataAccessObject:
    session = get_session()
    return ProductDataAccessObject(session)
