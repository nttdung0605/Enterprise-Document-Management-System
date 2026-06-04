import sqlite3
import unittest


class TestQuota(
    unittest.TestCase
):

    def test_department_quota(self):

        conn = sqlite3.connect(
            "server/db/edms.db"
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                quota_used,
                quota_max
            FROM departments
            WHERE id = 1
            """
        )

        used, max_quota = (
            cursor.fetchone()
        )

        self.assertLessEqual(
            used,
            max_quota
        )

        conn.close()


if __name__ == "__main__":
    unittest.main()