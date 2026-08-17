from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("test_rest.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            phone REAL NOT NULL,
            status TEXT NOT NULL)
    """)
    conn.commit()
    return conn

@app.route("/clients", methods=["GET"])
def get_clients():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"clients": clients}), 200

@app.route("/clients/<int:client_id>", methods=["GET"])
def get_client(client_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id))
    client = cursor.fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(client)), 200

@app.route("/clients", methods=["POST"])
def create_clients():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    status = data.get("status", "active")

    if not name or not email or not phone:
        return jsonify({"error": "Name, email and phone"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clients (name, phone, email, status)
        VALUES (?, ?, ?, ?)
    """, (name, phone, email, status))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"message": "Client created", "id": new_id}), 201

@app.route("/clients/<int:client_id>", methods=["PATCH"])
def update_client(client_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    data = request.get_json()
    name = data.get("name", client["name"])
    email = data.get("email", client["email"])
    phone = data.get("phone", client["phone"])
    status = data.get("status", client["status"])

    cursor.execute("""
        UPDATE clients SET name=?, phone=?, email=?, status=?
        WHERE id=?
    """, (name, email, phone, status, client_id))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Client {client_id} updated"}), 200

@app.route("/clients/<int:client_id>", methods=["DELETE"])
def delete_clients(client_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Client {client_id} deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)