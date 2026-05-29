from functools import wraps
from flask import session, redirect, url_for, jsonify, request
import jwt
import datetime
from flask import Flask

app = Flask(__name__)
SECRET_KEY = "kalikeng_secret_2026"

def create_token(username, role):
    payload = {
        "user": username,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm = "HS256")
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = ["HS256"])
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
            token = token [7:]
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(payload, *args, **kwargs)
    return decorated

USERS = {
    "thandi": {"password": "mofokeng2026", "role": "admin"},
    "samuel": {"password": "mokwena2026", "role": "user"}
}
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username").lower()
    password = data.get("password", "")
    if username in USERS and USERS[username]["password"] == password:
        token = create_token(username, USERS[username]["role"])
        return jsonify({"token":token, "user": username}), 200
    return jsonify({"error": "Invalid credintials"}), 401

@app.route("/api/profile")
@token_required
def profile(payload):
    return jsonify({"user": payload["user"], "role": payload["role"]})

if __name__ == "__main__":
    app.run(debug=True)
    


        
