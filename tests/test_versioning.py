import sqlite3
import unittest


class TestVersioning(unittest.TestCase):

    def test_versions_created(self):

        conn = sqlite3.connect(
            "server/db/edms.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM document_versions
            """
        )

        count = cursor.fetchone()[0]

        self.assertGreaterEqual(
            count,
            2
        )

        conn.close()


if __name__ == "__main__":
    unittest.main()