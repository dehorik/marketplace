from core.database import Session
from core.database.interface_database import InterfaceDataBase


class ProductDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD-операций с товарами"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self):
        self.__session.commit()
        self.__cursor.close()

    def commit(self):
        self.__session.commit()

    def create(
            self,
            product_owner_id: int,
            product_name: str,
            product_price: float,
            product_description: str,
            product_photo_path: str
    ) -> list:
        self.__cursor.execute(
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

        return self.__cursor.fetchall()

    def read(self, product_id: int) -> tuple:
        self.__cursor.execute(
            """
                SELECT * 
                FROM product
                WHERE prduct_id = %s;
            """,
            [product_id]
        )

        return self.__cursor.fetchall()

    def update(self, product_id: int, **kwargs) -> list:
        # модель передаваемых в kwargs данных:
        # {имя_поля: новое значение...}

        set_data = ""
        for key, value in kwargs.items():
            set_data = set_data + f"{key} = {value}, "
        set_data = set_data[:-2]

        query_text = f"""
            UPDATE product 
            SET {set_data}
            WHERE product_id = %s
            RETURNING *;
        """

        self.__cursor.execute(query_text, [product_id])
        return self.__cursor.fetchall()

    def delete(self, product_id: int) -> list:
        self.__cursor.execute(
            """"
                DELETE 
                FROM product
                WHERE product_id = %s
                RETURNING *;
            """,
            [product_id]
        )
        return self.__cursor.fetchall()

    def update_catalog(self, amount: int, last_product_id: int) -> list:
        self.__cursor.execute(
            """
                SELECT product_id, product_name, product_price, product_photo_path
                FROM product
                WHERE product_id < %s
                ORDER BY product_id DESC
                LIMIT %s;
            """,
            [last_product_id, amount]
        )

        return self.__cursor.fetchall()
