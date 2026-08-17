from flask import Flask, request,jsonify,render_template
import sqlite3

app = Flask(__name__)

def get_clients():
    conn = sqlite3.connect("kalikeng.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return clients

@app.route("/api/clients", methods=["GET", "POST"])
def clients():
    if request.method == "GET":
        clients = get_clients()
        return jsonify(clients)
    if request.method == "POST":
        data = request.get_json()
        if not data or not data.get("name"):
            return jsonify({"error": "Name is required"}),400
        name = data["name"]
        amount = data.get("amount", 0)
        status = data.get("status", "Unpaid")
        conn = sqlite3.connect("kalikeng.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (name, amount, status) VALUES (?,?,?)",
                       (name, amount, status))
        conn.commit()
        conn.close()
        return jsonify({"message": "Clients created", "name": name}), 201

@app.route("/api/clients/<int:id>", methods=["DELETE"])
def delete_clients(id):
    conn = sqlite3.connect("kalikeng.db")
    cursor = conn. cursor()
    cursor.execute("SELECT * FROM clients WHERE id=?", (id,))
    client = cursor.fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "Client not found"}), 404
    
    cursor.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"}), 200

@app.route("/", methods=["GET"])
def home():
    return render_template("day42.html")

if __name__== "__main__":
    app.run(debug=True)