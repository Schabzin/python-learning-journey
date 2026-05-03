import sqlite3
conn = sqlite3.connect("books.db")
cursor = conn.cursor()

cursor.execute("SELECT isbn, title, publisher FROM books WHERE LOWER(title) LIKE '%imvunge%'")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT isbn, title, publisher FROM books WHERE LOWER(title) LIKE '%zihlangene%'")
for row in cursor.fetchall():
    print(row)

conn.close()