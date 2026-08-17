import sqlite3
from flask import Flask, request, jsonify
from collections import defaultdict
import time
from functools import wraps
import logging


app = Flask(__name__)
from config import ProductionConfig
app.config.from_object(ProductionConfig)
API_KEY = "separaka_api_key_2026"

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s"
)


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



@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Access denied"}), 403

@app.route("/crash")
def crash():
    raise Exception("Test crash")

if __name__ == "__main__":
    app.run()