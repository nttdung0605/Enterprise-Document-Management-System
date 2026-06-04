import sqlite3
conn = sqlite3.connect("db/edms.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
for (t,) in cur.fetchall():
    print("==", t, "==")
    cols = [c[1] for c in conn.execute(f"PRAGMA table_info({t})")]
    print("|".join(cols))
    for row in conn.execute(f"SELECT * FROM {t}"):
        print(row)
conn.close()