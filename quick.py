import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_name ON platforms(name)")
conn.commit()
conn.close()
print("Unique constraint added")