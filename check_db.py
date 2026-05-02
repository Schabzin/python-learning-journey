import sqlite3

conn = sqlite3.connect("books.db")
cursor = conn.cursor()
cursor.execute("SELECT publisher, COUNT(*) as total FROM books GROUP BY publisher ORDER BY total DESC")
results = cursor.fetchall()
total = 0
for r in results:
    print(f"{r[0]}: {r[1]} books")
    total += r[1]
print(f"\nGRAND TOTAL: {total} books")
conn.close()