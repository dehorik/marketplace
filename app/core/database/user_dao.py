from datetime import date

from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class UserDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с пользователями"""

    def __init__(self, session: Session):
        self.__session = session

    def __execute(
            self,
            query: str,
            params: list | None = None,
            fetchone: bool = False
    ) -> list | tuple:
        """
        :param query: sql запрос
        :param params: параметры для подстановки в запрос
        :param fetchone: если True, возвращает одну строку; если False — все строки
               (для запросов, которые не возвращают данные, параметр игнорируется)
        """

        try:
            cursor = self.__session.get_cursor()
            cursor.execute(query, params)

            if cursor.description:
                return cursor.fetchone() if fetchone else cursor.fetchall()
            else:
                return []
        finally:
            cursor.close()

    def create(
            self,
            username: str,
            hashed_password: str,
            current_date: date
    ) -> tuple:
        return self.__execute(
            query="""
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
                    has_photo;
            """,
            params=[username, hashed_password, current_date],
            fetchone=True
        )

    def read(self, user_id: int) -> tuple:
        return self.__execute(
            query="""
                SELECT 
                    user_id, 
                    role_id, 
                    username, 
                    email, 
                    registration_date,
                    has_photo
                FROM users
                WHERE user_id = %s; 
            """,
            params=[user_id],
            fetchone=True
        )

    def update(
            self,
            user_id: int,
            clear_email: bool = False,
            clear_photo: bool = False,
            role_id: int | None = None,
            username: str | None = None,
            hashed_password: str | None = None,
            email: str | None = None,
            has_photo: bool | None = None
    ) -> tuple:
        if not any([clear_email, clear_photo, role_id, username, hashed_password, email, has_photo]):
            return self.__execute(
                query="""
                    SELECT 
                        user_id,
                        role_id, 
                        username,
                        email,
                        registration_date,
                        has_photo
                    FROM users
                    WHERE user_id = %s;
                """,
                params=[user_id],
                fetchone=True
            )

        fields = []
        params = []

        if role_id:
            fields.append("role_id = %s")
            params.append(role_id)

        if username:
            fields.append("username = %s")
            params.append(username)

        if hashed_password:
            fields.append("hashed_password = %s")
            params.append(hashed_password)

        if clear_email:
            fields.append("email = NULL")
        elif email:
            fields.append("email = %s")
            params.append(email)

        if clear_photo:
            fields.append("has_photo = FALSE")
        elif has_photo:
            fields.append("has_photo = TRUE")

        query = f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE user_id = %s
            RETURNING 
                user_id,
                role_id, 
                username,
                email,
                registration_date,
                has_photo;
        """
        params.append(user_id)

        return self.__execute(query=query, params=params, fetchone=True)

    def delete(self, user_id: int) -> tuple:
        return self.__execute(
            query="""
                DELETE
                FROM users
                WHERE user_id = %s
                RETURNING 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    has_photo;
            """,
            params=[user_id],
            fetchone=True
        )

    def get_user_by_username(self, username: str) -> tuple:
        # извлекается хеш пароля!

        return self.__execute(
            query="""
                SELECT 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    has_photo,
                    hashed_password
                FROM users
                WHERE username = %s;
            """,
            params=[username],
            fetchone=True
        )

    def get_users(self, min_role_id: int = 2) -> list:
        """
        :param min_role_id: параметр, указывающий, от какой роли
               будут отбираться аккаунты (включительно)
        """

        return self.__execute(
            query="""
                SELECT
                    users.user_id,
                    role.role_id,
                    role.role_name,
                    users.username,
                    users.has_photo
                FROM 
                    users INNER JOIN role
                    ON users.role_id = role.role_id
                WHERE role.role_id >= %s
                ORDER BY role.role_id DESC, users.user_id ASC;
            """,
            params=[min_role_id]
        )

    def set_role(self, username: str, role_id: int, request_sender_id: int) -> tuple:
        """
        Установка роли пользователю по юзернейму.
        Отправитель запроса не может устанавливать роль самому себе.

        :param username: юзернейм пользователя
        :param role_id: role_id будущей роли пользователя
        :param request_sender_id: user_id отправителя запроса
        """

        return self.__execute(
            query="""
                UPDATE users 
                SET role_id = %s
                WHERE username = %s AND user_id != %s;
                
                SELECT
                    users.user_id,
                    role.role_id,
                    role.role_name,
                    users.username,
                    users.has_photo
                FROM 
                    users INNER JOIN role
                    ON users.role_id = role.role_id
                WHERE users.username = %s AND users.user_id != %s;
            """,
            params=[role_id, username, request_sender_id, username, request_sender_id],
            fetchone=True
        )


def get_user_dao() -> UserDataAccessObject:
    session = get_session()
    return UserDataAccessObject(session)
