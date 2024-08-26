from core.database.session_factory import Session
from core.database.interface_database import InterfaceDataBase

class UserDataBase(InterfaceDataBase):
    """Класс для выполнения CRUD операций с пользователями"""

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

    def create(self, user_name: str, user_password: str) -> list:
        self._cursor.execute(
            """
                INSERT INTO users
                    (user_name, user_password)
                VALUES
                    (%s, %s)
                RETURNING 
                    user_id,
                    role_id, 
                    user_name,
                    user_email,
                    user_photo_path;
            """,
            [user_name, user_password]
        )

        return self._cursor.fetchall()

    def read(self, user_id: int) -> list:
        self._cursor.execute(
            """
                SELECT user_id, role_id, user_name, user_email, user_photo_path
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

    def check_user_name(self, user_name: str) -> list:
        self._cursor.execute(
            """
                SELECT *
                FROM users
                WHERE user_name = %s;
            """,
            [user_name]
        )

        return self._cursor.fetchall()

    def login_user(self, user_name: str, hashed_user_password: str) -> list:
        self._cursor.execute(
            """
                SELECT user_id, role_id, user_name, user_email, user_photo_path
                FROM users
                WHERE user_name = %s AND user_password = %s;
            """,
            [user_name, hashed_user_password]
        )

        return self._cursor.fetchall()
