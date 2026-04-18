from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    company = "Kalikeng Trading and Projects CC"
    year = 2026
    return render_template("index.html", company=company, year=year)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/clients")
def clients():
    clients = [
        {"name": "Botebo-Tsebo Seconday", "amount": 50000, "status": "Paid"},
        {"name": "Thandukwazi Seconday", "amount": 70000, "status": "Unpaid"},
        {"name": "Thabeng Primary", "amount": 100000, "status": "Paid"},
        {"name": "Rutasetjhaba Secondary", "amount": 150000, "status": "Unpaid"}
    ]
    return render_template("clients.html")

@app.route("/client/<name>")
def client(name):
    return f"Client: {name}"

@app.route("/status")
def status():
    return "System running - Kalikeng API v1.0"

if __name__ == "__main__":
    app.run(debug=True)