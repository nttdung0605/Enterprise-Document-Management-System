from db.database import (
    Database
)


class DocumentService:

    def __init__(self):

        self.db = Database()

    def upload_document(
        self,
        filename,
        session
    ):

        conn = (
            self.db.get_connection()
        )

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO documents
                (
                    filename,
                    department_id
                )
                VALUES (?, ?)
                """,
                (
                    filename,
                    session[
                        "department_id"
                    ]
                )
            )

            document_id = (
                cursor.lastrowid
            )

            cursor.execute(
                """
                INSERT INTO
                document_versions
                (
                    document_id,
                    version_num,
                    uploaded_by,
                    filepath,
                    filesize,
                    checksum,
                    status
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    document_id,
                    1,
                    session[
                        "user_id"
                    ],
                    "fake/path",
                    0,
                    "fake_checksum",
                    "pending"
                )
            )

            conn.commit()

            return True

        except Exception as e:

            conn.rollback()

            print(
                "[UPLOAD ERROR]",
                e
            )

            return False

        finally:

            conn.close()

    def list_pending(
        self,
        department_id
    ):

        conn = (
            self.db.get_connection()
        )

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                dv.id,
                d.filename,
                u.username,
                dv.status
            FROM
            document_versions dv

            JOIN documents d
            ON d.id = dv.document_id

            JOIN users u
            ON u.id = dv.uploaded_by

            WHERE
            dv.status='pending'
            AND
            d.department_id=?
            """,
            (department_id,)
        )

        rows = (
            cursor.fetchall()
        )

        conn.close()

        return rows