import sqlite3

conn = sqlite3.connect("taxi.db")
conn.execute("DELETE FROM taxis WHERE plate = 'DUPETEST GP'")
conn.execute("DELETE FROM users WHERE username IN ('dupetest1', 'dupetest2')")
conn.commit()
conn.close()
print("Cleaned up")
