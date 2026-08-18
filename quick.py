import sqlite3
conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("SELECT plate, prdp_expiry FROM taxis WHERE plate = 'TEST01 GP'")
print(cursor.fetchall())
conn.close()