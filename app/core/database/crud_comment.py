from core.database.interface_database import InterfaceDataBase
from core.database import Session


class CommentDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD-операций с комментариями"""

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
            user_id: int,
            product_id: int,
            comment_text: str,
            comment_rating: int,
            comment_photo_path: str | None = None
    ):
        self.__cursor.execute(
            """
                INSERT INTO comment (
                    user_id,
                    product_id,
                    comment_date,
                    comment_text,
                    comment_rating,
                    comment_photo_path
                )
                VALUES (%s, %s, CURRENT DATE, %s, %s, %s)
                RETURNING *;
            """,
            [user_id, product_id, comment_text, comment_rating, comment_photo_path]
        )
        return self.__cursor.fetchall()

    def read(self, product_id):
        self.__cursor.execute(
            """
                SELECT 
                    user_name, 
                    user_photo_path, 
                    comment_date, 
                    comment_text, 
                    comment_rating, 
                    comment_photo_path
                FROM product
                    INNER JOIN comment USING(product_id)
                    INNER JOIN user USING(user_id)
                WHERE product_id = %s
                ORDER BY comment_date DESC;
            """,
            [product_id]
        )
        return self.__cursor.fetchall()

    def update(
            self,
            comment_id: int,
            comment_text: str,
            comment_rating: int,
            comment_photo_path: str | None = None
    ):
        self.__cursor.execute(
            """
                UPDATE product 
                SET
                    comment_date = CURRENT DATE,
                    comment_text = %s,
                    comment_rating = %s,
                    comment_photo_path = %s
                WHERE comment_id = %s
                RETURNING *;
            """,
            [comment_text, comment_rating, comment_photo_path, comment_id]
        )
        return self.__cursor.fetchall()

    def delete(self, comment_id):
        self.__cursor.execute(
            """
                DELETE 
                FROM comment
                WHERE comment_id = %s
                RETURNING *;
            """,
            [comment_id]
        )
