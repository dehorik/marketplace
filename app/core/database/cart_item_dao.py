from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class CartItemDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с товарами в корзине"""

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

    def create(self, user_id: int, product_id: int) -> tuple:
        return self.__execute(
            query="""
                INSERT INTO cart_item (user_id, product_id)
                VALUES (%s, %s)
                RETURNING *;
            """,
            params=[user_id, product_id],
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
                cart_item.cart_item_id,
                cart_item.user_id,
                cart_item.product_id,
                product.name,
                product.price
            FROM 
                cart_item INNER JOIN product USING(product_id)     
        """]
        params = []

        if last_id:
            query_parts.append("""
                WHERE cart_item.user_id = %s AND cart_item.cart_item_id < %s
                ORDER BY cart_item.cart_item_id DESC
                LIMIT %s;
            """)
            params.extend([user_id, last_id, amount])
        else:
            query_parts.append("""
                WHERE cart_item.user_id = %s
                ORDER BY cart_item.cart_item_id DESC
                LIMIT %s;
            """)
            params.extend([user_id, amount])

        return self.__execute(query="".join(query_parts), params=params)

    def update(self):
        raise NotImplementedError("update is not supported for cart items")

    def delete(self, cart_item_id: int, user_id: int) -> tuple:
        return self.__execute(
            query="""
                DELETE 
                FROM cart_item
                WHERE cart_item_id = %s AND user_id = %s
                RETURNING *; 
            """,
            params=[cart_item_id, user_id],
            fetchone=True
        )


def get_cart_item_dao() -> CartItemDataAccessObject:
    session = get_session()
    return CartItemDataAccessObject(session)
