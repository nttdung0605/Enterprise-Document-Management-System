from typing import Literal
import uuid


class AuthService:

    def __init__(self) -> None:
        self.users: dict[str, str] = {
            "admin": "123456",
            "dung": "123"
        }

        self.sessions = {}

    def login(
        self,
        username,
        password
    ) -> tuple[Literal[True], str] | tuple[Literal[False], None]:
        if (
            username in self.users
            and
            self.users[username]
            == password
        ):
            token = str(
                uuid.uuid4()
            )

            self.sessions[token] = (
                username
            )

            return True, token

        return False, None

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