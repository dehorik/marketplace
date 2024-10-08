from core.settings import config
from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class CommentDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с отзывами под товарами"""

    def __init__(self, session: Session = Session()):
        self.__session = session
        self._cursor = session.get_cursor()

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
            has_photo: bool = False,
            comment_content_path: str = config.COMMENT_CONTENT_PATH
    ) -> list:
        if has_photo:
            self._cursor.execute(
                """
                    INSERT INTO comment (
                        user_id,
                        product_id,
                        comment_rating,
                        comment_date,
                        comment_text
                    )
                    VALUES (%s, %s, %s, CURRENT_DATE, %s)
                    RETURNING comment_id;
                """,
                [
                    user_id,
                    product_id,
                    comment_rating,
                    comment_text
                ]
            )

            comment_id = self._cursor.fetchone()[0]
            photo_path = f"{comment_content_path}/{comment_id}"

            self._cursor.execute(
                """
                    UPDATE comment 
                        SET photo_path = %s
                    WHERE comment_id = %s
                    RETURNING *;
                """,
                [photo_path, comment_id]
            )
        else:
            self._cursor.execute(
                """
                    INSERT INTO comment (
                        user_id,
                        product_id,
                        comment_rating,
                        comment_date,
                        comment_text
                    )
                    VALUES (%s, %s, %s, CURRENT_DATE, %s)
                    RETURNING *;
                """,
                [
                    user_id,
                    product_id,
                    comment_rating,
                    comment_text
                ]
            )

        return self._cursor.fetchall()

    def read(
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
                    users.username,
                    users.photo_path,
                    comment.comment_rating,
                    comment.comment_date,
                    comment.comment_text,
                    comment.photo_path   
                FROM users 
                    INNER JOIN comment USING(user_id)
                    INNER JOIN product USING(product_id)
                {condition}
                ORDER BY comment.comment_id DESC
                LIMIT {amount};
            """
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
                set_values += f"{key} = '{value}', "
            elif value is None:
                set_values += f"{key} = NULL, "
            else:
                set_values += f"{key} = {value}, "
        else:
            set_values += "comment_date = CURRENT_DATE"

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

    def delete_all_comments(self, product_id: int) -> list:
        """Удаление всех отзывов под товаром"""

        self._cursor.execute(
            """
                DELETE
                FROM comment
                WHERE product_id = %s
                RETURNING *;
            """,
            [product_id]
        )

        return self._cursor.fetchall()
