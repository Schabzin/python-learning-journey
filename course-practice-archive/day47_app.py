from flask import Flask, jsonify, request
import os
import sqlite3
import bcrypt
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv

SECRET_KEY = "kalikeng_secret_2026"

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback")
    DATABASE = os.environ.get("DATABASE_URL", "kalikeng.db")
    JWT_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

app = Flask(__name__)
app.config["SECRET_KEY"]= os.environ.get("SECRET_KEY", "fallback_key")
app.config["DATABASE"] = os.environ.get("DATABASE_URL", "kalikeng.db")
app.config["DEBUG"] = os.environ.get("DEBUG", "False").lower() == "true"
app.config["JWT_HOURS"] = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

def create_token(username, role):
    payload = {
        "user": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=app.config["JWT_HOURS"])
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
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

@app.route("/api/config-test", methods=["GET"])
@token_required
def config_test(payload):
    return jsonify({
        "user": payload["user"],
        "role": payload["role"],
    })

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").lower().strip()
    password = data.get("password", "")
    conn = sqlite3.connect(app.config["DATABASE"])
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

if __name__ == "__main__":
    app.run(debug=True)