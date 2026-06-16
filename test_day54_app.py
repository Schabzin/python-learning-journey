from flask import Flask, jsonify, request
import sqlite3, datetime, jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "secret_key_2026"

def get_db():
    db_name = app.config.get("DATABASE", "products.db")
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL)
    """)
    conn.commit()
    return conn

def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/products", methods=["GET"])
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"products": products}), 200
    
@app.route("/products", methods=["POST"])
def create_products():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    category = data.get("category")
    if not name or not price or not category:
        return jsonify({"error": "Name, price and category required"}), 400
    conn = get_db()
    cursor = conn. cursor()
    cursor.execute("""
        INSERT INTO products (name, price, category)
        VALUES (?, ?, ?)
    """, (name, price, category))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Product created", "id": new_id}), 201


@app.route("/products/<int:product_id>", methods=["GET"])
@token_required
def get_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(dict(product)), 200

if __name__ == "__main__":
    app.run(debug=True)

