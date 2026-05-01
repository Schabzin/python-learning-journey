import sqlite3

conn = sqlite3.connect("books.db")
cursor = conn.cursor()
cursor.execute("SELECT publisher, COUNT(*) FROM books GROUP BY publisher")
results = cursor.fetchall()
for r in results:
    print(f"{r[0]}: {[1]} books")
conn.close