from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class CommentDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с отзывами под товарами"""

    def __init__(self, session: Session):
        self.__session = session
        self._cursor = session.get_cursor()

    def __del__(self):
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
            [user_id, product_id, comment_text, comment_rating, comment_photo_path]
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

    def update(
            self,
            comment_id: int,
            comment_text: str | None = None,
            comment_rating: int | None = None,
            comment_photo_path: str | None = None
    ) -> list:
        params = {
            "comment_text": comment_text,
            "comment_rating": comment_rating,
            "comment_photo_path": comment_photo_path
        }
        params = {key: value for key, value in params.items() if value is not None}

        set_values = ""
        for key, value in params.items():
            if type(value) is str:
                set_values = set_values + f"{key} = '{value}', "
            else:
                set_values = set_values + f"{key} = {value}, "
        set_values = set_values[:-2]

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
