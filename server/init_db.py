import sqlite3
import os


def execute_sql_file(conn, path) -> None:
    with open(path, "r", encoding="utf-8") as file:
        sql = file.read()
    conn.executescript(sql)


def main() -> None:
    db_path: str = os.path.join("db", "edms.db")

    # If the database exists, remove it so init is idempotent.
    # This avoids errors like "index ... already exists" on re-run.
    if os.path.exists(db_path):
        os.remove(db_path)

    conn: sqlite3.Connection = sqlite3.connect(db_path)

    execute_sql_file(conn, "db/schema.sql")
    execute_sql_file(conn, "db/seed.sql")

    conn.commit()
    conn.close()

    print("Database initialized")


if __name__ == "__main__":
    main()