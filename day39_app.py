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
    

if __name__ =="__main__":
    app.run(debug=True)