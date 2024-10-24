from core.database.session_factory import Session, get_session
from core.database.interface_dao import InterfaceDataAccessObject


class UserDataAccessObject(InterfaceDataAccessObject):
    """Класс для выполнения crud операций с пользователями"""

    def __init__(self, session: Session):
        print("start")
        self.__session = session
        self.__cursor = session.get_cursor()

    def __del__(self):
        print("stop")
        self.close()

    def close(self) -> None:
        self.__cursor.close()

    def commit(self) -> None:
        self.__session.commit()

    def create(self, username: str, hashed_password: str) -> list:
        self.__cursor.execute(
            """
                INSERT INTO users (
                    role_id, 
                    username, 
                    hashed_password,
                    registration_date
                )
                VALUES
                    (1, %s, %s, CURRENT_DATE)
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

        return self.__cursor.fetchall()

    def read(self, user_id: int) -> list:
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

        return self.__cursor.fetchall()

    def update(self, user_id: int, **kwargs) -> list:
        if not kwargs:
            self.__cursor.execute(
                f"""
                    SELECT 
                        user_id,
                        role_id, 
                        username,
                        email,
                        registration_date,
                        photo_path
                    FROM users
                    WHERE user_id = {user_id};
                """
            )

            return self.__cursor.fetchall()

        set_values = ""
        for key, value in kwargs.items():
            if type(value) is str:
                set_values += f"{key} = '{value}', "
            elif value is None:
                set_values += f"{key} = NULL, "
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

        return self.__cursor.fetchall()

    def delete(self, user_id: int) -> list:
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

        return self.__cursor.fetchall()

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

    def get_user_by_username(self, username: str) -> list:
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

        return self.__cursor.fetchall()

    def set_role(self, user_id: int, role_id: int) -> list:
        self.__cursor.execute(
            """
                UPDATE users
                    SET role_id = %s
                WHERE user_id = %s
                RETURNING
                    user_id,
                    role_id, 
                    username,
                    email,
                    registration_date,
                    photo_path;
            """,
            [role_id, user_id]
        )

        return self.__cursor.fetchall()


def get_user_dao() -> UserDataAccessObject:
    session = get_session()
    return UserDataAccessObject(session)
