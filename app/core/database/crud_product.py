from core.database.abstract_database import AbstractDataBase


class CRUDproduct(AbstractDataBase):
    """
    Класс для выполнения CRUD-операций с товарами
    """

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def get_last_products(self) -> list:
        self.cursor.execute(
            """
            SELECT * from product
            ORDER BY product_id DESC;
            """
        )
        return self.cursor.fetchall()





