import sqlite3
from flask import Flask, request, jsonify
from collections import defaultdict
import time
from functools import wraps

app = Flask(__name__)
API_KEY = "separaka_api_key_2026"


def get_db():
    conn = sqlite3.connect("day53.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        status TEXT DEFAULT 'active')
    """)
    conn.commit()
    return conn

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-key")
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

request_counts = defaultdict(list)

def rate_limit(max_requests=10, window=60):
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

@app.route("/clients", methods=["GET"])
@require_api_key
@rate_limit(max_requests=5, window=60)
def get_clients():
    return jsonify({"clients": []}), 200

if __name__ == "__main__":
    app.run(debug=True)