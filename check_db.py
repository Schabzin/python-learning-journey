import sqlite3
import sys

name = sys.argv[1]
conn = sqlite3.connect(f"file:{name}?mode=ro", uri=True)

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for (table,) in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
    print(table, count, columns)

conn.close()