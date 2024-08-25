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
            comment_text: str | None,
            comment_rating: int,
            comment_photo_path: str | None
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

    # def read(
    #         self,
    #         product_id: int,
    #         amount: int,
    #         last_comment_id: int | None = None
    # ) -> list:
    #     """
    #     Для получения последних отзывов под товаром
    #
    #     :param product_id: id товара
    #     :param amount: количество отдаваемых отзывов
    #     :param last_comment_id: comment_id последнего отзыва из прошлой подгрузки;
    #            если это первый запрос на подгрузку отзывов, то не передавать ничего
    #     :return: список отзывов
    #     """
    #
    #     if last_comment_id:
    #         self._cursor.execute(
    #             """
    #                 SELECT
    #                     comment.user_id,
    #                     user_name,
    #                     user_photo_path,
    #                     comment_id,
    #                     comment_date,
    #                     comment_text,
    #                     comment_rating,
    #                     comment_photo_path
    #                 FROM product
    #                     INNER JOIN comment USING(product_id)
    #                     INNER JOIN user USING(user_id)
    #                 WHERE product_id = %s AND comment_id < %s
    #                 ORDER BY comment_id DESC
    #                 LIMIT %s;
    #             """,
    #             [product_id, last_comment_id, amount]
    #         )
    #
    #         return self._cursor.fetchall()
    #
    #     else:
    #         self._cursor.execute(
    #             """
    #                 SELECT
    #                     comment.user_id,
    #                     user_name,
    #                     user_photo_path,
    #                     comment_id,
    #                     comment_date,
    #                     comment_text,
    #                     comment_rating,
    #                     comment_photo_path
    #                 FROM product
    #                     INNER JOIN comment USING(product_id)
    #                     INNER JOIN user USING(user_id)
    #                 WHERE product_id = %s
    #                 ORDER BY comment_id DESC
    #                 LIMIT %s;
    #             """,
    #             [product_id, amount]
    #         )
    #
    #         return self._cursor.fetchall()

    def update(
            self,
            comment_id: int,
            comment_text: str,
            comment_rating: int,
            comment_photo_path: str | None
    ) -> list:
        self._cursor.execute(
            """
                UPDATE product 
                SET
                    comment_date = CURRENT_DATE,
                    comment_text = %s,
                    comment_rating = %s,
                    comment_photo_path = %s
                WHERE comment_id = %s
                RETURNING *;
            """,
            [comment_text, comment_rating, comment_photo_path, comment_id]
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
