from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
from functools import wraps
import sqlite3
import bcrypt
import jwt
import datetime
import os
from setup_taxi_db import init_db, create_default_taxis, create_default_users, add_created_at_column

init_db()
create_default_users()
create_default_taxis()
add_created_at_column()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "separaka_taxi_2026")

def get_db():
    conn = sqlite3.connect("/data/taxi.db")
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def check_trial(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT created_at FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if not user or not user["created_at"]:
        return True, 30
    created = datetime.datetime.fromisoformat(user["created_at"])
    days_used = (datetime.datetime.now() - created).days
    days_remaining = 30 - days_used
    return days_remaining > 0, days_remaining

@app.route("/trial-expired")
@login_required
def trial_expired():
    return render_template("taxi_trial_expired.html", user=session["user"])



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
    
    trial_active, days_remaining = check_trial(session["user"])
    if not trial_active:
        return redirect(url_for("trial_expired"))
    
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
                           today=today,
                           days_remaining=days_remaining)

@app.route("/api/taxis", methods=["GET"])
@login_required
def get_taxis():
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

@app.route("/driver")
@login_required
def driver_dashboard():
    if session["role"] != "driver":
        return redirect(url_for("dashboard"))
    
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.status,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id
            AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
            AND dt.date = ?
        WHERE t.driver_username = ?
        GROUP BY t.id
    """, (today, today, session["user"]))

    taxi = cursor.fetchone()
    display_name = taxi["driver_name"] if taxi else session["user"]
    conn.close()

    return render_template("taxi_driver.html",
                           user=display_name,
                           taxi=dict(taxi) if taxi else None,
                           today=today)

@app.route("/api/deposit", methods=["POST"])
@login_required
def log_deposit():
    amount = request.form.get("number")
    if not amount:
        flash("Please enter a deposit amount", "error")
        return redirect(url_for("driver_dashboard"))
    
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM taxis WHERE driver_username = ?", (session["user"],))
    taxi = cursor.fetchone()

    if taxi:
        cursor.execute("""
            SELECT id FROM daily_targets WHERE taxi_id = ? AND date = ?
        """, (taxi["id"], today))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE daily_targets SET collected_amount = ?
                WHERE taxi_id = ? AND date = ?
            """, (float(amount), taxi["id"], today))
        else:
            cursor.execute("""
                INSERT INTO daily_targets (taxi_id, date, collected_amount)
                VALUES (?, ?, ?)
            """, (taxi["id"], today, float(amount)))
        conn.commit()
        conn.close()
        flash("Deposit logged successfully", "success")
        return redirect(url_for("driver_dashboard"))
    else:
        conn.close()
        flash("No taxi found for your account", "error")
        return redirect(url_for("driver_dashboard"))
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        errors = []
        if not username:
            errors.append("Username is required")
        if len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if not password:
            errors.append("Password is required")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")

        if errors:
            return render_template("taxi_register.html", errors=errors)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return render_template("taxi_register.html",
                errors=["Username already taken"])
        
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, hashed, "owner"))
            conn.commit()
            conn.close()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("taxi_register.html",
                errors=["Username already taken"])
        
    return render_template("taxi_register.html")

@app.route("/api/driver/taxi", methods=["GET"])
@login_required
def get_my_taxi():
    if session["role"] != "driver":
        return jsonify({"error": "Access denied"}), 403
    
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.status,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id
            AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
            AND dt.date = ?
        WHERE t.driver_name = ?
        GROUP BY t.id
    """, (today, today, session["user"]))

    taxi = cursor.fetchone()
    conn.close()

    if not taxi:
        return jsonify({"error": "No taxi found"}), 404
    
    return jsonify(dict(taxi)), 200

@app.route("/admin/routes", methods=["GET"])
@owner_required
def manage_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    routes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_routes_admin.html", routes=routes)

@app.route("/admin/routes/add", methods=["POST"])
@owner_required
def add_route():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Route name is required", "error")
        return redirect(url_for("manage_routes"))
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO routes (name) VALUES (?)", (name,))
        conn.commit()
        flash(f"Route '{name}' added", "success")
    except sqlite3.IntegrityError:
        flash("Route already exists", "error")
    conn.close()
    return redirect(url_for("manage_routes"))

@app.route("/admin/routes/delete/<int:route_id>", methods=["POST"])
@owner_required
def delete_route(route_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routes WHERE id = ?", (route_id,))
    conn.commit()
    conn.close()
    flash("Route deleted", "success")
    return redirect(url_for("manage_routes"))

@app.route("/admin/taxis", methods=["GET"])
@owner_required
def manage_taxis():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxis WHERE owner_id = ?", (session["user_id"],))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_admin_taxis.html", taxis=taxis)

@app.route("/admin/taxi/add", methods=["POST"])
@owner_required
def add_taxi():
    plate = request.form.get("plate", "").strip()
    driver_name = request.form.get("driver_name", "").strip()
    driver_username = request.form.get("driver_username", "").strip()
    password = request.form.get("password", "").strip()

    if not plate or not driver_name or not driver_username or not password:
        flash("All fields are required", "error")
        return redirect(url_for("manage_taxis"))
    
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO taxis (plate, driver_name, driver_username, owner_id)
            VALUES (?, ?, ?, ?)
        """, (plate, driver_name, driver_username, session["user_id"]))
    except sqlite3.IntegrityError:
        flash("Taxi plate already exists", "error")
        conn.close()
        return redirect(url_for("manage_taxis"))
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (driver_username, hashed, "driver"))
    except sqlite3.IntegrityError:
        flash("Username already taken", "error")
        conn.close()
        return redirect(url_for("manage_taxis"))
    conn.commit()
    conn.close()
    return redirect(url_for("manage_taxis"))

@app.route("/api/target", methods=["POST"])
@login_required
def daily_target():
    amount = request.form.get("number")
    taxi_id = request.form.get("taxi_id")

    if not taxi_id or not amount:
        flash("Taxi and target amount are required", "error")
        return redirect(url_for("dashboard"))
    
    today = datetime.date.today().isoformat()
    conn =get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM daily_targets WHERE taxi_id = ? AND date = ?
    """, (taxi_id, today))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE daily_targets SET target_amount = ?
            WHERE taxi_id = ? AND date = ?
        """, (float(amount), taxi_id, today))

    else:
        cursor.execute("""
            INSERT INTO daily_targets (taxi_id, date, target_amount)
            VALUES (?, ?, ?)
        """, (taxi_id, today, float(amount)))

    conn.commit()
    conn.close()
    flash("Target updated successfully", "success")
    return redirect(url_for("dashboard"))




@app.route("/day57c")
@login_required
def day5c():
    return render_template("day57c.html")

@app.route("/day58")
@login_required
def day58():
    return render_template("day58.html")
      
if __name__ == "__main__":
    app.run(debug=True)
