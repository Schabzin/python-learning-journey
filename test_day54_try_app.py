from flask import Flask, jsonify, create_token, get_db, request
import sqlite3, jwt
import datetime
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "separaka_secret_key_2026"

@app.route("/products", methods=["GET"])
def products(client):
    response = client.get("/products")
    assert response.status_code == 200

@app.route("/products", methods=["POST"])
def products(client):
    response = client.post("/products",
            headers={"name": "Pen", "price": 3.50, "category": "Stationery"})
    assert response.status_code == 201

@app.route("/products/int:<id>", methods=["GET"])
def product(client):
    response = client.get("/products_id",
            json={"error", []})
    assert response.status_code == 404

    token = create_token("username", "role"),
    create_token = ("sechaba", "owner")

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

if __name__ == "__main__":
    app.run(debug=True)
    

