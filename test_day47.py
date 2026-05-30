from  flask import Flask, jsonify
from dotenv import load_dotenv
import os
import sqlite3


app = Flask(__name__)
load_dotenv()

secret = os.environ.get("SECRET_KEY", "kalikeng2026")
database = os.environ.get("DATABASE_URL", "test_day47.db")
debug = os.environ.get("DEBUG", "False")
jwt_hours = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback")
app.config["DATABASE"] = os.environ.get("DATABASE_URL")
app.config["DEBUG"] = os.environ.get("DEBUG","False")
app.config["JWT_HOURS"] = os.environ.get("JWT_EXPIRY_HOURS", "24")

def get_db():
    conn = sqlite3.connet(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/config")
def config():
    return jsonify({
        "secret_key": app.config["SECRET_KEY"],
        "database": app.config["DATABASE"],
        "debug": app.config["DEBUG"],
        "jwt_hours": app.config["JWT_HOURS"]
    })

if __name__ == "__main__":
    app.run(debug=True)