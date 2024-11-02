import os

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
                VALUES (%s, %s, %s, NOW(), %s)
                RETURNING *;
            """,
            [user_id, product_id, rating, text]
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
            amount: int = 10,
            last_id: int | None = None
    ) -> list:
        condition = f"""
            WHERE product.product_id = {product_id}
        """

        if last_id:
            condition += f"AND comment.comment_id < {last_id}"

        self.__cursor.execute(
            f"""
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
                {condition}
                ORDER BY comment.comment_id DESC
                LIMIT {amount};
            """
        )

        return self.__cursor.fetchall()

    def update(
            self,
            comment_id: int,
            user_id: int,
            rating: int | None = None,
            text: str | None = None,
            photo_path: str | None = None
    ) -> tuple:
        if not any([rating, text, photo_path]):
            self.__cursor.execute(
                """
                    SELECT *
                    FROM comment
                    WHERE comment_id = %s AND user_id = %s;
                """,
                [comment_id, user_id]
            )

            return self.__cursor.fetchone()

        fields = {
            key: value
            for key, value in {
                "rating": rating,
                "text": text,
                "photo_path": photo_path
            }.items()
            if value is not None
        }

        set_values = ""
        for key, value in fields.items():
            if type(value) is str and value.lower() == "null":
                set_values += f"{key} = NULL, "
            elif type(value) is str:
                set_values += f"{key} = '{value}', "
            else:
                set_values += f"{key} = {value}, "
        else:
            set_values += "creation_date = NOW()"

        self.__cursor.execute(
            f"""
                UPDATE comment 
                SET {set_values}            
                WHERE comment_id = {comment_id} AND user_id = {user_id}
                RETURNING *;
            """
        )

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
                WHERE product_id IS NULL
                RETURNING *;
            """,
        )

        return self.__cursor.fetchall()


def get_comment_dao() -> CommentDataAccessObject:
    session = get_session()
    return CommentDataAccessObject(session)
