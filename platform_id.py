import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("SELECT plate, driver_name, platform_id FROM taxis WHERE plate = 'NEW123'")
print(cursor.fetchone())