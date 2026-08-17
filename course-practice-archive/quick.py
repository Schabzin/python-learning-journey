import sqlite3
conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("UPDATE users SET email = ? WHERE username = ?", ("jake_real_email@example.com", "jake_username"))
conn.commit()
conn.close()
print("Email updated")