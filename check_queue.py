"""check_queue.py -- quick look at what's currently in the queue."""
import sqlite3

DB_PATH = r"C:\Users\Sechaba\Desktop\python\taxi.db"

conn = sqlite3.connect(DB_PATH)
rows = conn.execute(
    "SELECT id, taxi_id, platform_id, layer, position, status FROM queue WHERE status = 'waiting'"
).fetchall()
conn.close()

for row in rows:
    print(row)