import unittest
import socket


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000


class TestDepartmentPermission(
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

    def test_cross_department_download(self):

        login = self.send_cmd(
            "LOGIN staff_hr 123456"
        )

        token = (
            login.split("|")[1]
        )

        result = self.send_cmd(
            f"DOWNLOAD {token} report.pdf"
        )

        self.assertIn(
            result,
            [
                "ACCESS_DENIED",
                "VERSION_NOT_FOUND"
            ]
        )


if __name__ == "__main__":
    unittest.main()