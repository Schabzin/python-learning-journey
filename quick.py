import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM password_resets")
print(cursor.fetchall())
conn.close()