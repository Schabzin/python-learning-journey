import sqlite3
from utils import get_db_path

conn = sqlite3.connect(get_db_path())
rows = conn.execute(
    "SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name"
).fetchall()
conn.close()

for name, sql in rows:
    print(sql)
    print()