import sqlite3
conn = sqlite3.connect("taxi.db")
conn.execute("UPDATE users SET created_at = '2026-05-23T00:00:00' WHERE username = 'chahane'")
conn.commit()
conn.close()
print("Done")