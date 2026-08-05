import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("UPDATE users SET email = ? WHERE username = ?", ("schabzin18@gmail.com", "chahane"))
conn.commit()
conn.close()
print("Email updated")