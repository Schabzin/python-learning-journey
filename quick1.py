import sqlite3
conn = sqlite3.connect("textbooks.db")
cursor = conn.cursor()
cursor.execute("SELECT title, price FROM books LIMIT 5")
print(cursor.fetchall())
conn.close()