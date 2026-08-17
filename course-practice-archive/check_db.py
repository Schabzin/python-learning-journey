import sqlite3

conn = sqlite3.connect('taxi.db')
cursor = conn.cursor()
cursor.execute("SELECT plate, driver_username, driver_name FROM taxis")
results = cursor.fetchall()
for row in results:
    print(row)
conn.close()