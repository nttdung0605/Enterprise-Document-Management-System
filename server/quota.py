from db.database import (
    Database
)

class QuotaService:

    def __init__(self):

        self.db = Database()

    def check_user_quota(
        self,
        user_id,
        filesize
    ):

        conn = (
            self.db.get_connection()
        )

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT
                personal_quota_max,
                personal_quota_used
                FROM users
                WHERE id=?
                """,
                (user_id,)
            )

            result = cursor.fetchone()
            if result is None:
                return False
            personal_quota_max, personal_quota_used = result
            if personal_quota_used + filesize > personal_quota_max:
                return False
            return True
        except Exception as e:
            print(
                "[QUOTA ERROR]",
                e
            )
            return False
        
    def check_department_quota(
        self,
        department_id,
        filesize
    ):
        conn = (
            self.db.get_connection()
        )
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT
                quota_max,
                quota_used
                FROM departments
                WHERE id=?
                """,
                (department_id,)
            )
            result = cursor.fetchone()
            if result is None:
                return False
            quota_max,quota_used = result
            if quota_used + filesize > quota_max:
                return False
            return True
        except Exception as e:
            print(
                "[QUOTA ERROR]",
                e
            )
            return False

    
            