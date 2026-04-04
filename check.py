import sqlite3
conn = sqlite3.connect("kalikeng.db")
print(conn.execute("PRAGMA table_info(clients)").fetchall())