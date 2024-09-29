from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class CommentDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с отзывами под товарами"""

    def __init__(self, session: Session = Session()):
        self.__session = session
        self._cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self.__session.commit()
        self._cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(
            self,
            user_id: int,
            product_id: int,
            comment_rating: int,
            comment_text: str | None = None,
            comment_photo_path: str | None = None
    ) -> list:
        self._cursor.execute(
            """
                INSERT INTO comment (
                    user_id,
                    product_id,
                    comment_date,
                    comment_text,
                    comment_rating,
                    comment_photo_path
                )
                VALUES (%s, %s, CURRENT_DATE, %s, %s, %s)
                RETURNING *;
            """,
            [
                user_id,
                product_id,
                comment_text,
                comment_rating,
                comment_photo_path
            ]
        )

        return self._cursor.fetchall()

    def read(self, product_id):
        self._cursor.execute(
            """
                SELECT * 
                FROM comment 
                WHERE product_id = %s;
            """,
            [product_id]
        )

        return self._cursor.fetchall()

    def update(self, comment_id: int, **kwargs) -> list:
        if not kwargs:
            self._cursor.execute(
                """
                    SELECT *
                    FROM comment
                    WHERE comment_id = %s;
                """,
                [comment_id]
            )

            return self._cursor.fetchall()

        set_values = ""
        for key, value in kwargs.items():
            if type(value) is str:
                set_values = set_values + f"{key} = '{value}', "
            elif value is None:
                set_values = set_values + f"{key} = NULL, "
            else:
                set_values = set_values + f"{key} = {value}, "
        else:
            set_values = set_values + "comment_date = CURRENT_DATE"

        self._cursor.execute(
            f"""
                UPDATE comment 
                    SET {set_values}            
                WHERE comment_id = %s
                RETURNING *;
            """,
            [comment_id]
        )

        return self._cursor.fetchall()

    def delete(self, comment_id: int) -> list:
        self._cursor.execute(
            """
                DELETE 
                FROM comment
                WHERE comment_id = %s
                RETURNING *;
            """,
            [comment_id]
        )

        return self._cursor.fetchall()

    def get_comment_item_list(
            self,
            product_id: int,
            amount: int = 10,
            last_comment_id: int = None
    ) -> list:
        if last_comment_id:
            condition = f"""
                WHERE product.product_id = {product_id} 
                AND comment.comment_id < {last_comment_id}
            """
        else:
            condition = f"WHERE product.product_id = {product_id}"

        self._cursor.execute(
            f"""
                SELECT 
                    comment.comment_id, 
                    users.user_id,
                    product.product_id, 
                    users.user_name,
                    users.user_photo_path,
                    comment.comment_rating,
                    comment.comment_date,
                    comment.comment_text,
                    comment.comment_photo_path   
                FROM users 
                    INNER JOIN comment USING(user_id)
                    INNER JOIN product USING(product_id)
                {condition}
                ORDER BY comment.comment_id DESC
                LIMIT {amount};
            """
        )

        return self._cursor.fetchall()
