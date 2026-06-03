import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect("records.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL)
    """)
    for i in range(1, 51):
        cursor.execute("INSERT OR IGNORE INTO products (name, price, category) VALUES (?, ?, ?)",
                       (f"Product {i}", i * 10, "General"))
    conn.commit()
    return conn
                       
         
@app.route("/products")
def products():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM products LIMIT ? OFFSET ?",(per_page, offset))
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    total_pages = (total + per_page - 1) // per_page

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "products": products    
    })

if __name__ == "__main__":
    app.run(debug=True)
