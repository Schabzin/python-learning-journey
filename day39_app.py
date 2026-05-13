from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("day39.html")

@app.route("/api/clients")
def get_clients():
    conn = sqlite3.connect("kalikeng.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clients)

@app.route("/clients")
def clients():
    return render_template("day39b.html")

@app.route("/api/summary")
def get_summary():
    conn = sqlite3.connect("kalikeng.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM clients")
    revenue = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM clients WHERE status='Paid'")
    paid = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM clients WHERE status='Unpaid'")
    unpaid = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        "total": total,
        "revenue": revenue,
        "paid": paid,
        "unpaid": unpaid
    })

@app.route("/dashboard")
def dashboard():
    return render_template("day39c.html")

@app.route("/day40")
def day40():
    return render_template("day40.html")

@app.route("/day40b")
def day40b():
    return render_template("day40b.html")

@app.route("/day40c")
def day40c():
    return render_template("day40c.html")

@app.route("/day41")
def day41():
    return render_template("day41.html")

@app.route("/day41b")
def day41b():
    return render_template("day41b.html")
     

if __name__ =="__main__":
    app.run(debug=True)