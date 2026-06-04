import socket
import sqlite3
import unittest
import os
import hashlib


SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

TEST_FILE = "reject_test.txt"


class TestReject(
    unittest.TestCase
):

    def setUp(self):

        with open(
            TEST_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                "Reject Test"
            )

    def tearDown(self):

        if os.path.exists(
            TEST_FILE
        ):
            os.remove(
                TEST_FILE
            )

    def connect(self):

        s = socket.socket()

        s.connect(
            (
                SERVER_IP,
                SERVER_PORT
            )
        )

        return s

    def login(
        self,
        username,
        password
    ):

        s = self.connect()

        cmd = (
            f"LOGIN {username} {password}"
        )

        s.send(
            cmd.encode()
        )

        response = (
            s.recv(4096)
            .decode()
        )

        s.close()

        self.assertTrue(
            response.startswith(
                "LOGIN_SUCCESS"
            )
        )

        return (
            response.split("|")[1]
        )

    def upload(
        self,
        token,
        filepath
    ):

        filesize = (
            os.path.getsize(
                filepath
            )
        )

        filename = (
            os.path.basename(
                filepath
            )
        )

        s = self.connect()

        cmd = (
            f"UPLOAD "
            f"{token} "
            f"{filename} "
            f"{filesize}"
        )

        s.send(
            cmd.encode()
        )

        ready = (
            s.recv(4096)
            .decode()
        )

        self.assertEqual(
            ready,
            "READY_UPLOAD"
        )

        with open(
            filepath,
            "rb"
        ) as f:

            data = f.read()

        s.send(data)

        ready_checksum = (
            s.recv(4096)
            .decode()
        )

        self.assertEqual(
            ready_checksum,
            "READY_CHECKSUM"
        )

        checksum = hashlib.sha256(
            data
        ).hexdigest()

        s.send(
            (
                f"CHECKSUM {checksum}"
            ).encode()
        )

        result = (
            s.recv(4096)
            .decode()
        )

        s.close()

        self.assertIn(
            "UPLOAD_SUCCESS",
            result
        )

    def test_upload_reject_flow(
        self
    ):

        #
        # Staff upload
        #

        staff_token = (
            self.login(
                "staff_it",
                "123456"
            )
        )

        self.upload(
            staff_token,
            TEST_FILE
        )

        #
        # Manager login
        #

        manager_token = (
            self.login(
                "manager_it",
                "123456"
            )
        )

        #
        # LIST_PENDING
        #

        s = self.connect()

        s.send(
            (
                f"LIST_PENDING "
                f"{manager_token}"
            ).encode()
        )

        pending = (
            s.recv(4096)
            .decode()
        )

        s.close()

        self.assertIn(
            TEST_FILE,
            pending
        )

        #
        # Lấy version_id mới nhất
        #

        DB_PATH = (
            "server/db/edms.db"
        )

        conn = sqlite3.connect(
            DB_PATH
        )

        conn.row_factory = (
            sqlite3.Row
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM document_versions
            ORDER BY id DESC
            LIMIT 1
            """
        )

        version_id = (
            cursor.fetchone()["id"]
        )

        conn.close()

        #
        # REJECT
        #

        s = self.connect()

        s.send(
            (
                f"REJECT "
                f"{manager_token} "
                f"{version_id}"
            ).encode()
        )

        result = (
            s.recv(4096)
            .decode()
        )

        s.close()

        self.assertEqual(
            result,
            "REJECT_SUCCESS"
        )

        #
        # Verify DB
        #

        conn = sqlite3.connect(
            DB_PATH
        )

        conn.row_factory = (
            sqlite3.Row
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT status
            FROM document_versions
            WHERE id=?
            """,
            (version_id,)
        )

        status = (
            cursor.fetchone()["status"]
        )

        conn.close()

        self.assertEqual(
            status,
            "rejected"
        )


if __name__ == "__main__":
    unittest.main()