from flask import Flask, jsonify, request
import sqlite3, jwt, datetime, os
from functools import wraps

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "day54_secret")

def get_db():
    db_name = app.config.get("DATABASE", "items.db")
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL)
    """)
    conn.commit()
    return conn

@app.route("/items", methods=["GET"])
def get_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"items": items}), 200

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    name = data.get("name") if data else None
    price = data.get("price")
    category = data.get("category")

    if not name or not price or not category:
        return jsonify({"error": "Name, price and category required"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO items (name, price, category) VALUES (?, ?, ?)",
                       (name, price, category))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "Item created", "id": new_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "Item already exists"}), 400


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

@app.route("/items/<int:item_id>", methods=["GET"])
@token_required
def get_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(dict(item)), 200



if __name__ == "__main__":
    app.run(debug=True)


