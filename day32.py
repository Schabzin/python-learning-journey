from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Kalikeng!"

@app.route("/about")
def about():
    return "Kalikeng Trading and Projects CC"

@app.route("/client/<name>")
def client(name):
    return f"Client: {name}"

@app.route("/status")
def status():
    return "System running - Kalikeng API v1.0"

if __name__ == "__main__":
    app.run(debug=True)