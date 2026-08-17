from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt, os, datetime
from functools import wraps

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "day53_secret")
CORS(app, origins=["http://separaka.co.za"])

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

def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.route("/token", methods=["GET"])
def get_token():
    username = request.args.get("username", "test")
    role = request.args.get("role", "user")
    token = create_token(username, role)
    return jsonify({"token": token}), 200

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.route("/users")
def users():
    users = [
        {"id": 1, "username": "sechaba", "role": "owner"},
        {"id": 2, "username": "oupa", "role": "driver"}
    ]
    return jsonify({"users": users}), 200

@app.route("/profile")
@token_required
def profile():
    return jsonify({
        "username": request.current_user["username"],
        "role": request.current_user["role"]
    }), 200

if __name__ == "__main__":
    app.run(debug=True)

