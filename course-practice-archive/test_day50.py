from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("test_pagination.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL)
    """)
    
    for i in range (1, 31):
        cursor.execute("INSERT OR IGNORE INTO products (name, price, category) VALUES (?,?,?)",
                       (f"Product{i}", i * 10, "General"))
    conn.commit()
    return conn

@app.route("/products")
def products():
    page = request.args.get("page",1, type=int)
    search = request.args.get("search", "", type=str)
    sort = request.args.get("sort", "", type=str)
    per_page = 10
    offset = (page - 1) * per_page
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE 1=1")
    total = cursor.fetchone()[0]
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")

    query += " LIMIT ? OFFSET ?"
    params.append(per_page)
    params.append(offset)
    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()]

    total_pages = (total + per_page - 1) // per_page

    return jsonify({
        "page":page,
        "per_page":per_page,
        "total":total,
        "total_pages":total_pages,
        "products":products
    })

if __name__ == "__main__":
    app.run(debug=True)