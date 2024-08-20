from core.database.abstract_database import AbstractDataBase


class Product(AbstractDataBase):
    """
    Класс для выполнения CRUD-операций с товарами
    """

    def create(
            self,
            product_owner_id: int,
            product_name: str,
            product_price: float,
            product_description: str,
            product_photo: str
    ) -> None:
        self.cursor.execute(
            """
                INSERT INTO product 
                    (product_owner_id, product_name, product_price, product_description, product_photo)
                VALUES
                    (%s, %s, %s, %s, %s);
            """,
            [product_owner_id, product_name, product_price, product_description, product_photo]
        )

    def read(self, product_id: int) -> tuple:
        self.cursor.execute(
            """
                SELECT * 
                FROM product
                WHERE prduct_id = %s;
            """,
            [product_id]
        )
        return self.cursor.fetchone()

    def update(self, product_id: int, **kwargs) -> None:
        # модель передаваемых в kwargs данных:
        # {имя_поля: новое значение...}

        set_data = ""
        for key, value in kwargs.items():
            set_data = set_data + f"{key} = {value}, "
        set_data = set_data[:-2]

        query_text = f"""
            UPDATE product SET {set_data}
            WHERE product_id = %s;
        """

        self.cursor.execute(query_text, [product_id])

    def delete(self, product_id: int) -> None:
        self.cursor.execute(
            """"
                DELETE 
                FROM product
                WHERE product_id = %s;   
            """,
            [product_id]
        )

    def get_last_products(self) -> list:
        self.cursor.execute(
            """
                SELECT * 
                FROM product
                ORDER BY product_id DESC
                LIMIT 50;
            """
        )
        return self.cursor.fetchall()

