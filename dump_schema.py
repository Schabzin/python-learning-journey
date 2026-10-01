import sqlite3

conn = sqlite3.connect(r"C:\Users\Sechaba\Desktop\python\taxi.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"\n--- {table} ---")
    cursor.execute(f"PRAGMA table_info({table})")
    for col in cursor.fetchall():
        print(col)
conn.close()