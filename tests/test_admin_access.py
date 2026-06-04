import unittest
import socket


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


class TestAdminAccess(
    unittest.TestCase
):

    def send_cmd(
        self,
        cmd
    ):

        s = socket.socket()

        s.connect(
            (
                SERVER_IP,
                SERVER_PORT
            )
        )

        s.send(
            cmd.encode()
        )

        data = (
            s.recv(
                4096
            )
            .decode()
        )

        s.close()

        return data

    def test_admin_can_list_all(self):

        login = self.send_cmd(
            "LOGIN admin 123456"
        )

        token = (
            login.split("|")[1]
        )

        result = self.send_cmd(
            f"LIST_DOCUMENTS {token}"
        )

        self.assertTrue(
            len(result) > 0
        )


if __name__ == "__main__":
    unittest.main()