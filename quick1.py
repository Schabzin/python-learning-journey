import sqlite3
conn = sqlite3.connect("textbooks.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT grade, COUNT(*) as count FROM books GROUP BY grade")
for row in cursor.fetchall():
    print(row["grade"], row["count"])
conn.close()