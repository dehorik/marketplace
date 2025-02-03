from datetime import date
from psycopg2 import ProgrammingError

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class CommentDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с отзывами под товарами"""

    def __init__(self, session: Session):
        self.__session = session

    def __execute(
            self,
            query: str,
            params: list | None = None,
            fetchone: bool = False
    ) -> list | tuple | None:
        cursor = self.__session.get_cursor()
        cursor.execute(query, params)

        try:
            data = cursor.fetchone() if fetchone else cursor.fetchall()
            cursor.close()

            return data
        except ProgrammingError:
            cursor.close()

    def create(
            self,
            user_id: int,
            product_id: int,
            rating: int,
            current_date: date,
            text: str | None = None,
            has_photo: bool = False
    ) -> tuple:
        return self.__execute(
            query="""
                INSERT INTO comment (
                    user_id,
                    product_id,
                    rating,
                    creation_date,
                    text,
                    has_photo
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *;
            """,
            params=[user_id, product_id, rating, current_date, text, has_photo],
            fetchone=True
        )

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
                users.has_photo,
                comment.rating,
                comment.creation_date,
                comment.text,
                comment.has_photo
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

        return self.__execute(query=query, params=params)

    def update(
            self,
            comment_id: int,
            user_id: int,
            current_date: date,
            clear_text: bool = False,
            clear_photo: bool = False,
            rating: int | None = None,
            text: str | None = None,
            has_photo: bool | None = None
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
            query += ", has_photo = FALSE"
        elif has_photo:
            query += ", has_photo = TRUE"

        query += """
            WHERE comment_id = %s AND user_id = %s
            RETURNING *;
        """
        params.extend([comment_id, user_id])

        return self.__execute(query=query, params=params, fetchone=True)

    def delete(self, comment_id: int, user_id: int) -> tuple:
        return self.__execute(
            query="""
                DELETE 
                FROM comment
                WHERE comment_id = %s AND user_id = %s
                RETURNING *;
            """,
            params=[comment_id, user_id],
            fetchone=True
        )

    def delete_undefined_comments(self) -> list:
        # удаление всех отзывов, у которых product_id или user_id равны null
        # null появляется вместо внешнего ключа,
        # если связанная запись была удалена из таблицы

        return self.__execute(
            query="""
                DELETE
                FROM comment
                WHERE product_id IS NULL or user_id IS NULL
                RETURNING *;
            """
        )


def get_comment_dao() -> CommentDataAccessObject:
    session = get_session()
    return CommentDataAccessObject(session)
