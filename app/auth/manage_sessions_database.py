from core.database import Session


class ManageSessionsDataBase:
    def __init__(self, session: Session):
        self.__session = session
        self._cursor = session.get_cursor()

    def __del__(self):
        self.close()

    def close(self):
        self._cursor.close()
        self.__session.commit()

    def commit(self):
        self.__session.commit()

    def set_session(self, session_key: str, user_id: int) -> list:
        self._cursor.execute(
            """
                INSERT INTO session
                    (session_key, user_id)
                VALUES
                    (%s, %s)
                RETURNING *;
            """,
            [session_key, user_id]
        )

        return self._cursor.fetchall()

    def get_user_by_session_key(self, session_key: str) -> list:
        self._cursor.execute(
            """
                SELECT users.user_id, role_id, user_name, user_email, user_photo_path
                FROM users
                    INNER JOIN session USING(user_id)
                WHERE session_key = %s;            
            """,
            [session_key]
        )

        return self._cursor.fetchall()

    def delete_session(self, session_key: str) -> list:
        self._cursor.execute(
            """
                DELETE 
                FROM session
                WHERE session_key = %s
                RETURNING *;
            """,
            [session_key]
        )

        return self._cursor.fetchall()
