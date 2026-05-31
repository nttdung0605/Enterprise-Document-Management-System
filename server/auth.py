import uuid

from db.database import (
    Database
)

class AuthService:
    def __init__(self):

        self.db = Database()

        self.sessions = {}

    def login(
        self,
        username,
        password
    ):

        conn = (
            self.db.get_connection()
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if (
            user
            and
            user["password_hash"]
            == password
        ):

            token = str(
                uuid.uuid4()
            )

            self.sessions[token] = {

                "user_id":
                user["id"],

                "username":
                user["username"],

                "role":
                user["role"],

                "department_id":
                user[
                    "department_id"
                ]
            }

            return (
                True,
                token
            )

        return (
            False,
            None
        )

    def logout(
        self,
        token
    ) -> bool:
        if token in self.sessions:
            del self.sessions[token]
            return True

        return False

    def is_authenticated(
        self,
        token
    ) -> bool:
        return (
            token in self.sessions
        )
    
    def get_session(
        self,
        token
    ):
    
        return self.sessions.get(
            token
        )