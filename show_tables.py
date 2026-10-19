import sqlite3

TABLES = ("trips", "daily_targets")

conn = sqlite3.connect("taxi.db")
rows = conn.execute(
    "SELECT name, sql FROM sqlite_master WHERE name IN (?, ?)",
    TABLES,
).fetchall()
conn.close()

for name, sql in rows:
    print(f"--- {name} ---")
    print(sql)
    print()

conn = sqlite3.connect("taxi.db")
for table in TABLES:
    print(f"=== {table} columns ===")
    for col in conn.execute(f"PRAGMA table_info({table})"):
        print(f"  {col[1]:<16} {col[2]:<10} default={col[4]}")
conn.close()