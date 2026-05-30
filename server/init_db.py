import sqlite3


def execute_sql_file(
    conn,
    path
):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        sql = file.read()

    conn.executescript(sql)


def main():

    conn = sqlite3.connect(
        "db/edms.db"
    )

    execute_sql_file(
        conn,
        "db/schema.sql"
    )

    execute_sql_file(
        conn,
        "db/seed.sql"
    )

    conn.commit()

    conn.close()

    print(
        "Database initialized"
    )


if __name__ == "__main__":
    main()