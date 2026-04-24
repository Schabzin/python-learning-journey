from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "kalikeng2026"

def get_clients():
    conn = sqlite3.connect("kalikeng.db")
    conn.row_factory=sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

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
    clients = get_clients()
    return render_template("clients.html", clients=clients)

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
        all_clients = get_clients()
        for client in all_clients:
            if client["name"].lower() == name:
                result = client
                break
    return render_template("search.html", result=result)

@app.route("/add_client", methods=["GET", "POST"])
def add_client():
    message = None
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        amount = float(request.form["amount"])
        status = request.form["status"]

        conn = sqlite3.connect("kalikeng.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (name, phone, amount, status)
            VALUES (?, ?, ?, ?) 
        """, (name, phone, amount, status))
        conn.commit()
        conn.close()

        flash("Client added successfully!", "success")
        return redirect(url_for("clients"))
    return render_template("add_client.html")

@app.route("/edit_client/<int:id>", methods=["GET", "POST"])
def edit_client(id):
    conn = sqlite3.connect("kalikeng.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        amount = float(request.form["amount"])
        status = request.form["status"]
        cursor.execute("""
            UPDATE clients SET name=?, phone=?, amount=?, status=?
            WHERE id=?
        """, (name, phone, amount, status, id))
        conn.commit()
        conn.close()
        flash("Client added successfully!", "success")
        return redirect(url_for("clients"))

    cursor.execute("SELECT * FROM clients WHERE id=?", (id,))
    client = cursor.fetchone()
    conn.close()
    return render_template("edit_client.html", client=client)   

@app.route("/delete_client/<int:id>")
def delete_client(id):
    conn = sqlite3.connect("kalikeng.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("clients"))     

if __name__ == "__main__":
    app.run(debug=True)