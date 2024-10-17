import os

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject
from core.settings import config


class CommentDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с отзывами под товарами"""

    def __init__(self, session: Session = get_session()):
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
            has_photo: bool = False
    ) -> list:
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

        if has_photo:
            comment_id = self._cursor.fetchone()[0]
            photo_path = os.path.join(
                config.COMMENT_CONTENT_PATH,
                str(comment_id)
            )

            self._cursor.execute(
                """
                    UPDATE comment 
                        SET photo_path = %s
                    WHERE comment_id = %s
                    RETURNING *;
                """,
                [photo_path, comment_id]
            )

        return self._cursor.fetchall()

    def read(
            self,
            product_id: int,
            amount: int = 10,
            last_comment_id: int | None = None
    ) -> list:
        condition = f"WHERE product.product_id = {product_id}"

        if last_comment_id:
            condition += f"AND comment.comment_id < {last_comment_id}"

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
                WHERE comment_id = {comment_id}
                RETURNING *;
            """
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

    def delete_undefined_comments(self) -> list:
        """
        Удаление всех отзывов, у которых отсутствует product_id,
        т.е удаление отзывов под удаленными товарами
        """

        self._cursor.execute(
            """
                DELETE
                FROM comment
                WHERE product_id IS NULL
                RETURNING *;
            """,
        )

        return self._cursor.fetchall()
