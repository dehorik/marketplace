from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class UserDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с пользователями"""

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

    def create(self, user_name: str, user_hashed_password: str) -> list:
        self._cursor.execute(
            """
                INSERT INTO users (
                    role_id, 
                    user_name, 
                    user_hashed_password
                )
                VALUES
                    (1, %s, %s)
                RETURNING 
                    user_id,
                    role_id, 
                    user_name,
                    user_email,
                    user_photo_path;
            """,
            [user_name, user_hashed_password]
        )

        return self._cursor.fetchall()

    def read(self, user_id: int) -> list:
        self._cursor.execute(
            """
                SELECT 
                    user_id, 
                    role_id, 
                    user_name, 
                    user_email, 
                    user_photo_path
                FROM users
                WHERE user_id = %s;
            """,
            [user_id]
        )

        return self._cursor.fetchall()

    def update(self):
        pass

    def delete(self):
        pass

    def get_user_by_user_name(self, user_name: str) -> list:
        #  для аутентификации, извлекается хеш пароля

        self._cursor.execute(
            """
                SELECT 
                    user_id,
                    role_id, 
                    user_name,
                    user_hashed_password,
                    user_email,
                    user_photo_path
                FROM users
                WHERE user_name = %s;
            """,
            [user_name]
        )

        return self._cursor.fetchall()
