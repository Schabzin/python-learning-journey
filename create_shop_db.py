import sqlite3

conn = sqlite3.connect("test_shop.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER
    )
""")

cursor.executemany("""
    INSERT INTO products (name, price, stock)
    VALUES (?, ?, ?)
""", [
    ("Milk", 34.50, 100),
    ("Coffee", 67.99, 50),
    ("Bread", 19.20, 200),
    ("Butter", 35.60, 75),
    ("Sugar", 78.23, 150)
])

conn.commit()
conn.close()
print("Database created!")