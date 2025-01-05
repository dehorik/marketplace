from datetime import date

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class UserDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с пользователями"""

    def __init__(self, session: Session):
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self) -> None:
        self.__cursor.close()

    def create(
            self,
            username: str,
            hashed_password: str,
            current_date: date
    ) -> tuple:
        self.__cursor.execute(
            """
                INSERT INTO users (
                    role_id, 
                    username, 
                    hashed_password,
                    registration_date
                )
                VALUES
                    (1, %s, %s, %s)
                RETURNING 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    photo_path;
            """,
            [username, hashed_password, current_date]
        )

        return self.__cursor.fetchone()

    def read(self, user_id: int) -> tuple:
        self.__cursor.execute(
            """
                SELECT 
                    user_id, 
                    role_id, 
                    username, 
                    email, 
                    registration_date,
                    photo_path
                FROM users
                WHERE user_id = %s;
            """,
            [user_id]
        )

        return self.__cursor.fetchone()

    def update(
            self,
            user_id: int,
            clear_email: bool = False,
            clear_photo: bool = False,
            role_id: int | None = None,
            username: str | None = None,
            hashed_password: str | None = None,
            email: str | None = None,
            photo_path: str | None = None
    ) -> tuple:
        if not any([clear_email, clear_photo, role_id, username, hashed_password, email, photo_path]):
            self.__cursor.execute(
                """
                    SELECT 
                        user_id,
                        role_id, 
                        username,
                        email,
                        registration_date,
                        photo_path
                    FROM users
                    WHERE user_id = %s;
                """,
                [user_id]
            )

            return self.__cursor.fetchone()

        query = """
            UPDATE users
            SET 
        """
        params = []

        if role_id:
            query += " role_id = %s, "
            params.append(role_id)

        if username:
            query += " username = %s, "
            params.append(username)

        if hashed_password:
            query += " hashed_password = %s, "
            params.append(hashed_password)

        if clear_email:
            query += " email = NULL, "
        elif email:
            query += " email = %s, "
            params.append(email)

        if clear_photo:
            query += " photo_path = NULL, "
        elif photo_path:
            query += " photo_path = %s, "
            params.append(photo_path)

        query = query[:-2] + """
            WHERE user_id = %s
            RETURNING 
                user_id,
                role_id, 
                username,
                email,
                registration_date,
                photo_path;
        """
        params.append(user_id)

        self.__cursor.execute(query, params)

        return self.__cursor.fetchone()

    def delete(self, user_id: int) -> tuple:
        self.__cursor.execute(
            """
                DELETE
                FROM users
                WHERE user_id = %s
                RETURNING 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    photo_path;
            """,
            [user_id]
        )

        return self.__cursor.fetchone()

    def get_user_by_username(self, username: str) -> tuple:
        # извлекается хеш пароля!

        self.__cursor.execute(
            """
                SELECT 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    photo_path,
                    hashed_password
                FROM users
                WHERE username = %s;
            """,
            [username]
        )

        return self.__cursor.fetchone()

    def get_users(self, min_role_id: int = 2) -> list:
        """
        :param min_role_id: параметр, указывающий, от какой роли
               будут отбираться аккаунты (включительно)
        """

        self.__cursor.execute(
            """
                SELECT
                    users.user_id,
                    role.role_id,
                    role.role_name,
                    users.username,
                    users.photo_path
                FROM 
                    users INNER JOIN role
                    ON users.role_id = role.role_id
                WHERE role.role_id >= %s
                ORDER BY role.role_id DESC;
            """,
            [min_role_id]
        )

        return self.__cursor.fetchall()


def get_user_dao() -> UserDataAccessObject:
    session = get_session()
    return UserDataAccessObject(session)
