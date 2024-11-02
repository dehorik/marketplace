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

    def commit(self) -> None:
        self.__session.commit()

    def create(self, username: str, hashed_password: str) -> tuple:
        self.__cursor.execute(
            """
                INSERT INTO users (
                    role_id, 
                    username, 
                    hashed_password,
                    registration_date
                )
                VALUES
                    (1, %s, %s, NOW())
                RETURNING 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    photo_path;
            """,
            [username, hashed_password]
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
            role_id: int | None = None,
            username: str | None = None,
            email: str | None = None,
            photo_path: str | None = None
    ) -> tuple:
        if not any([role_id, username, email, photo_path]):
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

        fields = {
            key: value
            for key, value in {
                "role_id": role_id,
                "username": username,
                "email": email,
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
            set_values = set_values[:-2]

        self.__cursor.execute(
            f"""
                UPDATE users
                SET {set_values}
                WHERE user_id = {user_id}
                RETURNING 
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    photo_path;
            """
        )

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

    def get_admins(self, role_id: int = 1) -> list:
        """
        :param role_id: параметр, указывающий, от какой роли
               будут отбираться аккаунты (не включительно)
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
                WHERE role.role_id > %s
                ORDER BY role.role_id DESC, users.username ASC;
            """,
            [role_id]
        )

        return self.__cursor.fetchall()

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


def get_user_dao() -> UserDataAccessObject:
    session = get_session()
    return UserDataAccessObject(session)
