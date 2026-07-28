import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(daily_targets)")
for col in cursor.fetchall():
    print(col)
conn.close()