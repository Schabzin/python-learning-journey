import sqlite3

conn = sqlite3.connect(r"C:\Users\Sechaba\Desktop\python\taxi.db")
print(conn.execute("SELECT id, plate FROM taxis").fetchall())
conn.close()