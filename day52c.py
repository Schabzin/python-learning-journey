from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
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
    conn.commit()
    return conn

@app.route("/drivers", methods=["GET"])
def get_drivers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers")
    drivers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"drivers": drivers}), 200

@app.route("/drivers/<int:driver_id>", methods=["GET"])
def get_driver(driver_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,))
    driver = cursor.fetchone()
    conn.close()
    if not driver:
        return jsonify({"error": "Driver not found"}), 404
    return jsonify(dict(driver)), 200

@app.route("/drivers", methods=["POST"])
def create_driver():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")
    license_number = data.get("license_number")
    status = data.get("status", "active")

    if not name or not phone or not license_number:
        return jsonify({"error": "Name, phone and license required"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO drivers (name, phone, license_number, status)
        VALUES (?, ?, ?, ?)
    """, (name, phone, license_number, status))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"message": "Driver created", "id": new_id}), 201

@app.route("/drivers/<int:driver_id>", methods=["PATCH"])
def update_driver(driver_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,))
    driver = cursor.fetchone()

    if not driver:
        conn.close()
        return jsonify({"error": "Driver not found"}), 404
    
    data = request.get_json()
    name = data.get("name", driver["name"])
    phone = data.get("phone", driver["phone"])
    license_number = data.get("license_number", driver["license_number"])
    status = data.get("status", driver["status"])

    cursor.execute("""
        UPDATE drivers SET name=?, phone=?, license_number=?, status=?
        WHERE id=?
    """, (name, phone, license_number, status, driver_id))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Driver {driver_id} updated"}), 200
                      
                    
@app.route("/drivers/<int:driver_id>", methods=["DELETE"])
def delete_driver(driver_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers WHERE id = ?", (driver_id,))
    driver = cursor.fetchone()
    if not driver:
        conn.close()
        return jsonify({"error": "Driver not found"}), 404
    cursor.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Driver {driver_id} deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
