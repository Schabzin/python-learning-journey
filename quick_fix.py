import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("UPDATE taxis SET platform_id = 1 WHERE plate = 'TESTQ01'")
conn.commit()
conn.close()
print("TESTQ01 updated")