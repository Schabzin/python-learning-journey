import datetime
import jwt
import os
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "day53_secret")

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

@app.route("/data", methods=["GET"])
@token_required
def get_data():
    return jsonify({"message": "Data accessed", "user": request.current_user}), 200

@app.route("/admin", methods=["GET"])
@owner_required
def get_admin():
    return jsonify({"error": "Data accessed", "user": request.current_user}), 200

@app.route("/token", methods=["GET"])
def get_token():
    username = request.args.get("username", "test")
    role = request.args.get("role", "user")
    token = create_token(username, role)
    return jsonify({"token": token}), 200

if __name__ == "__main__":
    app.run(debug=True)

