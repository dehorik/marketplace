from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase


class UserDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с пользователями"""

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

    def create(self, username: str, hashed_password: str) -> list:
        self._cursor.execute(
            """
                INSERT INTO users (
                    role_id, 
                    username, 
                    hashed_password
                )
                VALUES
                    (1, %s, %s)
                RETURNING 
                    user_id,
                    role_id, 
                    username,
                    email,
                    photo_path;
            """,
            [username, hashed_password]
        )

        return self._cursor.fetchall()

    def read(self, user_id: int) -> list:
        self._cursor.execute(
            """
                SELECT 
                    user_id, 
                    role_id, 
                    username, 
                    email, 
                    photo_path
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

    def get_user_by_username(self, username: str) -> list:
        #  для аутентификации, извлекается хеш пароля

        self._cursor.execute(
            """
                SELECT 
                    user_id,
                    role_id, 
                    username,
                    email,
                    photo_path,
                    hashed_password
                FROM users
                WHERE username = %s;
            """,
            [username]
        )

        return self._cursor.fetchall()

    def set_role(self, user_id: int, role_id: int) -> list:
        self._cursor.execute(
            """
                UPDATE users
                    SET role_id = %s
                WHERE user_id = %s
                RETURNING
                    user_id,
                    role_id, 
                    username,
                    email,
                    photo_path;
            """,
            [role_id, user_id]
        )

        return self._cursor.fetchall()
