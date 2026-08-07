import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("SELECT plate, platform_id FROM taxis")
print(cursor.fetchall())
conn.close()