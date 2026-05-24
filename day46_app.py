from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "kaliken_secret_2026"

def init_db():
    conn = sqlite3.connect("kalikeng.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_token(username, role):
    payload = {
        "user": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception as e:
        print(f"JWT Error: {e}")
        return None
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")

        if not token:
            return jsonify({"error": "Token missing"}), 401
        if token.startswith("Bearer "):
            token = token[7:]
        print(f"Token after strip: {token[:30]}...")

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return f(payload, *args, **kwargs)
    return decorated

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").lower().strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 character"}), 400
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        conn = sqlite3.connect("kalikeng.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hashed))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registration successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 409

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").lower().strip()
    password = data.get("password", "")

    conn = sqlite3.connect("kalikeng.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if bcrypt.checkpw(password.encode(), user["password"]):
        token = create_token(username, user["role"])
        return jsonify({"token": token, "user": username}), 200
    
    return jsonify({"error": "Invalid password"}), 401

@app.route("/api/profile", methods=["GET"])
@token_required
def profile(payload):
    return jsonify({
        "user": payload["user"],
        "role": payload["role"],
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True)