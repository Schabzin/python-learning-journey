"""
list_tables.py
Prints which database get_db_path() points at, and every table in it.
Read-only: it never changes anything.
"""
import sqlite3
from utils import get_db_path

path = get_db_path()
print("Database:", path)

conn = sqlite3.connect(path)
try:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
finally:
    conn.close()

for (name,) in rows:
    print(" -", name)
print(len(rows), "tables")