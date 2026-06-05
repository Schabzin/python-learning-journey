from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect("drivers.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            license_number TEXT NOT NULL,
            status TEXT NOT NULL)  
""")

@app.route("/drivers", methods=["GET"])
def get_drivers():
    return jsonify({"drivers": []}), 200

@app.route("/drivers/<int:driver_id>", methods=["GET"])
def get_driver(driver_id):
    return jsonify({"driver_id": driver_id}), 200

@app.route("/drivers", methods=["POST"])
def create_driver():
    data = request.get_json()
    return jsonify({"message": "User created"}), 201

@app.route("/drivers/<int:driver_id>", methods=["DELETE"])
def delete_driver(driver_id):
    return jsonify({"message": f"Driver {driver_id} deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)




