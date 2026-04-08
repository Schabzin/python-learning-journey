import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER
    )
""")
conn.commit()

products = [
    ("Pen", 5.50, 100),
    ("Notebook", 25.00, 50),
    ("Ruler", 8.75, 200)
]

cursor.executemany("""
    INSERT INTO products(name,price,stock)
    VALUES(?,?,?)
""", products)
conn.commit()

cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()