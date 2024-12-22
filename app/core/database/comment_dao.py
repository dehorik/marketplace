import os
from datetime import date

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject
from core.settings import config


class CommentDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с отзывами под товарами"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(
            self,
            user_id: int,
            product_id: int,
            rating: int,
            current_date: date,
            text: str | None = None,
            has_photo: bool = False
    ) -> tuple:
        self.__cursor.execute(
            """
                INSERT INTO comment (
                    user_id,
                    product_id,
                    rating,
                    creation_date,
                    text
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            """,
            [user_id, product_id, rating, current_date, text]
        )

        if has_photo:
            comment_id = self.__cursor.fetchone()[0]
            photo_path = os.path.join(
                config.COMMENT_CONTENT_PATH,
                str(comment_id)
            )

            self.__cursor.execute(
                """
                    UPDATE comment 
                    SET photo_path = %s
                    WHERE comment_id = %s
                    RETURNING *;
                """,
                [photo_path, comment_id]
            )

        return self.__cursor.fetchone()

    def read(
            self,
            product_id: int,
            amount: int = 15,
            last_id: int | None = None
    ) -> list:
        query = f"""
            SELECT 
                comment.comment_id, 
                users.user_id,
                product.product_id, 
                users.username,
                users.photo_path,
                comment.rating,
                comment.creation_date,
                comment.text,
                comment.photo_path   
            FROM users 
                INNER JOIN comment USING(user_id)
                INNER JOIN product USING(product_id)
        """
        params = []

        if last_id:
            query += """
                WHERE product.product_id = %s AND comment.comment_id < %s
                ORDER BY comment.comment_id DESC
                LIMIT %s;
            """
            params.extend([product_id, last_id, amount])
        else:
            query += """
                WHERE product.product_id = %s
                ORDER BY comment.comment_id DESC
                LIMIT %s;
            """
            params.extend([product_id, amount])

        self.__cursor.execute(query, params)

        return self.__cursor.fetchall()

    def update(
            self,
            comment_id: int,
            user_id: int,
            current_date: date,
            clear_text: bool = False,
            clear_photo: bool = False,
            rating: int | None = None,
            text: str | None = None,
            photo_path: str | None = None
    ) -> tuple:
        query = """
            UPDATE comment 
            SET creation_date = %s
        """
        params = [current_date]

        if rating:
            query += ", rating = %s"
            params.append(rating)

        if clear_text:
            query += ", text = NULL"
        elif text:
            query += ", text = %s"
            params.append(text)

        if clear_photo:
            query += ", photo_path = NULL"
        elif photo_path:
            query += ", photo_path = %s"
            params.append(photo_path)

        query += """
            WHERE comment_id = %s AND user_id = %s
            RETURNING *;
        """
        params.extend([comment_id, user_id])

        self.__cursor.execute(query, params)

        return self.__cursor.fetchone()

    def delete(self, comment_id: int, user_id: int) -> tuple:
        self.__cursor.execute(
            """
                DELETE 
                FROM comment
                WHERE comment_id = %s AND user_id = %s
                RETURNING *;
            """,
            [comment_id, user_id]
        )

        return self.__cursor.fetchone()

    def delete_undefined_comments(self) -> list:
        # удаление всех отзывов, у которых product_id или user_id равны null
        # null появляется вместо внешнего ключа,
        # если связанная запись была удалена из таблицы

        self.__cursor.execute(
            """
                DELETE
                FROM comment
                WHERE product_id IS NULL or user_id IS NULL
                RETURNING *;
            """,
        )

        return self.__cursor.fetchall()


def get_comment_dao() -> CommentDataAccessObject:
    session = get_session()
    return CommentDataAccessObject(session)
