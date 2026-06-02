from db.database import (
    Database
)


class AuditService:

    def __init__(self):

        self.db = Database()

    def log_action(
        self,
        action,
        user_id,
        version_id,
        client_ip
    ):

        conn = (
            self.db.get_connection()
        )

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO
                audit_logs
                (
                    action,
                    user_id,
                    version_id,
                    client_ip
                )
                VALUES
                (
                    ?, ?, ?, ?
                )
                """,
                (
                    action,
                    user_id,
                    version_id,
                    client_ip
                )
            )

            conn.commit()

        except Exception as e:

            print(
                "[AUDIT ERROR]",
                e
            )

            conn.rollback()

        finally:

            conn.close()

    def get_logs(self):
        
        conn = (
            self.db.get_connection()
        )
    
        cursor = conn.cursor()
    
        cursor.execute(
            """
            SELECT
                a.id,
                a.action,
                u.username,
                a.version_id,
                a.client_ip,
                a.action_time
            FROM audit_logs a
            JOIN users u
            ON u.id=a.user_id
            ORDER BY a.id DESC
            """
        )
    
        rows = (
            cursor.fetchall()
        )
    
        conn.close()
    
        return rows