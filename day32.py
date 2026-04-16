from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/clients")
def clients():
    return render_template("clients.html")

@app.route("/client/<name>")
def client(name):
    return f"Client: {name}"

@app.route("/status")
def status():
    return "System running - Kalikeng API v1.0"

if __name__ == "__main__":
    app.run(debug=True)