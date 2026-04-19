from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_clients():
    conn = sqlite3.connect("kalikeng.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

clients_list = [
    {"name": "Botebo-Tsebo Seconday", "amount": 50000, "status": "Paid"},
    {"name": "Thandukwazi Seconday", "amount": 70000, "status": "Unpaid"},
    {"name": "Thabeng Primary", "amount": 100000, "status": "Paid"},
    {"name": "Rutasetjhaba Secondary", "amount": 150000, "status": "Unpaid"}
]

@app.route("/dashboard")
def dashboard():
    clients = get_clients()
    total = sum(client["amount"] for client in clients)
    paid = sum(1 for client in clients if client["status"] == "Paid")
    unpaid = sum(1 for client in clients if client["status"] == "Unpaid")
    return render_template("dashboard.html",
                        clients=clients,
                        total=total,
                        paid=paid,
                        unpaid=unpaid)

@app.route("/clients")
def clients():
    return render_template("clients.html", clients=clients_list)

@app.route("/")
def home():
    company = "Kalikeng Trading and Projects CC"
    year = 2026
    return render_template("index.html", company=company, year=year)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/client/<name>")
def client(name):
    return f"Client: {name}"

@app.route("/status")
def status():
    return "System running - Kalikeng API v1.0"

@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        name = request.form["client_name"].lower()
        for client in clients_list:
            if client["name"].lower() == name:
                result = client
                break
    return render_template("search.html", result=result) 

if __name__ == "__main__":
    app.run(debug=True)