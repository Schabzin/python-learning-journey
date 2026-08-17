from flask import Flask, request, render_template
import sqlite3

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
    conn.commit()
    return conn

@app.route("/products")
def products():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    category = request.args.get("category", "", type=str)
    sort = request.args.get("sort", "id", type=str)
    order = request.args.get("order", "asc", type=str)
    allowed_sort = ["id", "name", "price", "category"]
    if sort not in allowed_sort:
        sort = "id"

    if order not in ["asc", "desc"]:
        order = "asc"
    per_page = 10
    offset = (page - 1) * per_page
    conn = sqlite3.connect("records.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()   
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    

    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")

    if category:
        query += " AND category = ?"
        params.append(category)

    query += f" ORDER BY {sort} {order} LIMIT ? OFFSET ?"
    params.append(per_page)
    params.append(offset)
    print(query)
    print(params)
    cursor.execute(query, params)
    products = [dict(row) for row in cursor.fetchall()] 

    count_query = "SELECT COUNT(*) FROM products WHERE 1=1"
    count_params = []

    
    if search:
        count_query += " AND name LIKE ?"
        count_params.append(f"%{search}%")

    if category:
        count_query += " AND category = ?"
        params.append(category)
        count_params.append(category)

    

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    

    return render_template("products_display.html",
        products=products,
        page=page,
        total_pages=total_pages,
        search=search,
        category=category,
        sort_by=sort,
        order=order)

if __name__ == "__main__":
    app.run(debug=True)
