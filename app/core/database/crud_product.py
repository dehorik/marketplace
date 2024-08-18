from app.core.database.abstract_database import AbstractDataBase
from app.core.database.session_factory import BaseSession


class CRUDproduct(AbstractDataBase):
    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def get_last_products(self) -> list:
        self._cursor.execute(
            """
            SELECT * from product
            ORDER BY product_id DESC;
            """
        )
        return self._cursor.fetchall()


session = BaseSession()
obj = CRUDproduct(session)
obj.get_last_products()
obj.close_cursor()
