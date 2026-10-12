"""
inspect_pings.py
Read-only: shows every GPS ping, and SQLite's own counter of the highest id
ever handed out. Use it to investigate missing pings.
"""
import sqlite3
from utils import get_db_path

path = get_db_path()
print("Database:", path)

conn = sqlite3.connect(path)
try:
    rows = conn.execute(
        "SELECT id, taxi_id, recorded_at, received_at FROM gps_pings ORDER BY id"
    ).fetchall()
    counter = conn.execute(
        "SELECT seq FROM sqlite_sequence WHERE name = 'gps_pings'"
    ).fetchone()
finally:
    conn.close()

print("Pings in table:", len(rows))
for row in rows:
    print(" ", row)
print("Highest id ever handed out:", counter[0] if counter else "no record")