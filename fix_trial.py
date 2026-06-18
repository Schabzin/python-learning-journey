import sqlite3
conn = sqlite3.connect("taxi.db")
conn.execute("UPDATE users SET created_at = NULL WHERE username = 'chahane'")
conn.commit()
conn.close()
print("Reset done")