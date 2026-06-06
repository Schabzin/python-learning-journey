from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
from functools import wraps
import sqlite3
import bcrypt
import jwt
import datetime
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "separaka_taxi_2026")

def get_db():
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "owner":
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode(), user["password"]):
            session["user"] = username
            session["role"] = user["role"]
            session["user_id"] = user["id"]
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "error")
        return redirect(url_for("login"))
    return render_template("taxi_login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required 
def dashboard():
    if session["role"] == "marshall":
        return redirect(url_for("marshall"))
    if session["role"] == "driver":
        return redirect(url_for("driver_dashboard"))
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.driver_name, t.status,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id
            AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
            AND dt.date = ?
        GROUP BY t.id
    """, (today, today))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_dashboard.html",
                           username=session["user"],
                           role=session["role"],
                           taxis=taxis,
                           today=today)

@app.route("/api/taxis", methods=["GET"])
@login_required
def get_taxis():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxis")
    taxis = [dict(t) for t in cursor.fetchall()]
    conn.close()
    return jsonify(taxis)

@app.route("/api/routes", methods=["GET"])
@login_required
def get_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    routes = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(routes)

@app.route("/api/trips", methods=["POST"])
@login_required
def log_trip():
    data = request.get_json()
    taxi_id = data.get("taxi_id")
    route_id = data.get("route_id")
    if not taxi_id or not route_id:
        return jsonify({"error": "Taxi and route required"}), 400
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trips (taxi_id, route_id, logged_by)
        VALUES (?, ?, ?)
    """, (taxi_id, route_id, session["user_id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Trip logged"}), 201

@app.route("/api/summary", methods=["GET"])
@login_required
def get_summary():
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.plate, t.driver_name,
                COUNT(tr.id) as trips,
                dt.target_amount, dt.collected_amount
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id
            AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
            AND dt.date = ?
        GROUP BY t.id
    """, (today, today))
    summary = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(summary)

@app.route("/marshall")
@login_required
def marshall():
    return render_template("taxi_marshall.html", user=session["user"])


if __name__ == "__main__":
    app.run(debug=True)
