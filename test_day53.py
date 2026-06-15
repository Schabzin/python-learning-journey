import sqlite3
from flask import Flask, request, jsonify
from functools import wraps
import jwt, datetime
from flask_cors import CORS
import time
from collections import defaultdict

app = Flask(__name__)
API_KEY = "api_key_2026"
SECRET_KEY = "separaka_secret_key_2026"
CORS(app)

def get_db():
    conn = sqlite3.connect("test_security.db")
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

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

request_counts = defaultdict(list)
    
def rate_limit(max_requests=5, window=60):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            request_counts[ip] = [t for t in request_counts[ip] if now - t < window]
            if len(request_counts[ip]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded"}), 429
            request_counts[ip].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator
     

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY,algorithms=["HS256"])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token required"}), 401
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("role") != "owner":
                return jsonify({"error": "Owner access required"}), 403
            request.current_user = payload
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)

    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.route("/token", methods={"GET"})
def get_token():
    username = request.args.get("username", "test")
    role = request.args.get("role", "user")
    token = create_token(username, role)
    return jsonify({"token": token}), 200

@app.route("/profile", methods=["GET"])
@token_required
def profile():
    return jsonify({
        "message": "Profile accessed",
        "user": request.current_user
    }), 200

@app.route("/admin", methods=["GET"])
@owner_required
def admin():
    return jsonify({
        "message": "Admin accessed",
        "user": request.current_user
    }), 200


@app.route("/products", methods=["GET"])
@require_api_key
@rate_limit(max_requests=5, window=60)
def get_products():
    return jsonify({"products": []}), 200


if __name__ == "__main__":
    app.run(debug=True)


