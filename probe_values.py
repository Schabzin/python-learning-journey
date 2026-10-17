import sqlite3
from utils import get_db_path

QUERIES = [
    "SELECT DISTINCT role FROM users",
    "SELECT DISTINCT status FROM taxis",
    "SELECT DISTINCT status FROM queue",
    "SELECT DISTINCT weekend_letter, ab_letter FROM taxis",
    "SELECT id, platform_id, name FROM layers",
    "SELECT id, name, rank_name FROM platforms",
]

conn = sqlite3.connect(get_db_path())
for sql in QUERIES:
    print(sql)
    print(conn.execute(sql).fetchall())
conn.close()