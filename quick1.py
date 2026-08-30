import sqlite3
conn = sqlite3.connect("taxi_backup_2026-08-30.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM taxis")
print(cursor.fetchone())
conn.close()