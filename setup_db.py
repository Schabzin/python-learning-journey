import sqlite3

conn = sqlite3.connect("books.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT,
        title TEXT,
        grade TEXT,
        subject TEXT,
        language TEXT,
        price REAL,
        book_type TEXT,
        publisher TEXT
    )
""")

conn.commit()
conn.close()
print("books.db created successfully!")