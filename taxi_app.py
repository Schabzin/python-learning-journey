from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
from functools import wraps
import sqlite3
import bcrypt
import jwt
import datetime
import os
from setup_taxi_db import init_db, create_default_taxis, create_default_users, add_created_at_column, add_platform_support
from flask import send_file
import io
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(messages)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")

    ]
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



init_db()
create_default_users()
create_default_taxis()
add_created_at_column()
add_platform_support()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "separaka_taxi_2026")

def get_db():
    if os.path.exists("/data"):
        conn = sqlite3.connect("/data/taxi.db")
    else:
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

def check_trial(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT created_at, paid_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return True, 30
    
    if user["paid_until"]:
        paid_until = datetime.datetime.fromisoformat(user["paid_until"])
        if datetime.datetime.now() < paid_until:
            return True, 999
        else:
            return False, 0
        
    if not user["created_at"]:
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

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("user") != "sechaba_admin":
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
    if session["user"] == "sechaba_admin":
        return redirect(url_for("admin_dashboard"))
    
    trial_active, days_remaining = check_trial(session["user"])
    if not trial_active:
        return redirect(url_for("trial_expired"))
    
    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    month_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id
            AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
            AND dt.date = ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (today, today, session["user_id"]))

    cursor.execute("""
        SELECT COUNT(tr.id) as week_trips, COALESCE(SUM(dt.collected_amount), 0) as week_collected
        FROM trips tr
        LEFT JOIN daily_targets dt ON tr.taxi_id = dt.taxi_id AND dt.date = DATE(tr.timestamp)
        WHERE DATE(tr.timestamp) >= ?
    """, (week_ago,))
    week_data = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(tr.id) as month_trips, COALESCE(SUM(dt.collected_amount), 0) as month_collected
        FROM trips tr
        LEFT JOIN daily_targets dt ON tr.taxi_id = dt.taxi_id AND dt.date = DATE(tr.timestamp)
        WHERE DATE(tr.timestamp) >= ?
    """, (month_ago,))
    month_data = cursor.fetchone()
    taxis = [dict(row) for row in cursor.fetchall()]

    for taxi in taxis:
        cursor.execute("""
            SELECT COUNT(tr.id) as week_trips, COALESCE(SUM(dt.collected_amount), 0) as week_collected
            FROM trips tr
            LEFT JOIN daily_targets dt ON tr.taxi_id = dt.taxi_id AND dt.date = DATE(tr.timestamp)
            WHERE tr.taxi_id = ? AND DATE(tr.timestamp) >= ?
        """, (taxi["id"], week_ago))
        taxi_week = cursor.fetchone()
        taxi["week_trips"] = taxi_week["week_trips"]
        taxi["week_collected"] = taxi_week["week_collected"]
        
    conn.close()
    return render_template("taxi_dashboard.html",
                           username=session["user"],
                           role=session["role"],
                           taxis=taxis,
                           today=today,
                           days_remaining=days_remaining,
                           week_data=week_data,
                           month_data=month_data)

@app.route("/api/taxis", methods=["GET"])
@login_required
def get_taxis():
    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    if session["role"] == "marshall":
        cursor.execute("""
            SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km,
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
    else:
        cursor.execute("""
            SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km,
                    COUNT(tr.id) as trips_today,
                    COALESCE(dt.target_amount, 750) as target,
                    COALESCE(dt.collected_amount, 0) as collected
            FROM taxis t
            LEFT JOIN trips tr ON t.id = tr.taxi_id
                AND DATE(tr.timestamp) = ?
            LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
                AND dt.date = ?
            WHERE t.owner_id = ?
            GROUP BY t.id
        """, (today, today, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]


    for taxi in taxis:
        cursor.execute("""
            SELECT COUNT(tr.id) as week_trips, COALESCE(SUM(dt.collected_amount), 0) as week_collected
            FROM trips tr
            LEFT JOIN daily_targets dt ON tr.taxi_id = dt.taxi_id AND dt.date = DATE(tr.timestamp)
            WHERE tr.taxi_id = ? AND DATE(tr.timestamp) >= ?
        """, (taxi["id"], week_ago))
        taxi_week = cursor.fetchone()
        taxi["week_trips"] = taxi_week["week_trips"]
        taxi["week_collected"] = taxi_week["week_collected"]
        
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
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    month_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate,t.driver_name, t.status,
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
                UPDATE daily_targets SET collected_amount = collected_amount + ?
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
@admin_required
def manage_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    routes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_routes_admin.html", routes=routes)

@app.route("/admin/routes/add", methods=["POST"])
@admin_required
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
@admin_required
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
    cursor.execute("SELECT * FROM platforms")
    platforms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_admin_taxis.html", taxis=taxis, platforms=platforms)

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
        logger.warning("Attempted to add taxi with plate that already exists: %s", plate)
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
        logger.warning("Attempted to add already-existing username: %s", driver_username)
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

@app.route("/api/km", methods=["POST"])
@owner_required
def update_km():
    taxi_id = request.form.get("taxi_id")
    new_km = request.form.get("current_km")
    manual_next_service = request.form.get("next_service_km", "").strip()

    if not taxi_id or not new_km:
        flash("Taxi and KM reading required", "error")
        return redirect(url_for("dashboard"))
    
    new_km = int(new_km)
    
    conn = get_db()
    cursor = conn.cursor()

    if manual_next_service.isdigit():
        new_next_service = int(manual_next_service)
    else:
        cursor.execute("SELECT next_service_km FROM taxis WHERE id = ?", (taxi_id,))
        taxi = cursor.fetchone()
        current_next_service = taxi["next_service_km"]

        if current_next_service == 0 or new_km >= current_next_service:
            new_next_service = new_km + 10000
        else:
            new_next_service = current_next_service

    cursor.execute(
        "UPDATE taxis SET current_km = ?, next_service_km = ? WHERE id = ?",
        (new_km, new_next_service, taxi_id)
    )
    conn.commit()
    conn.close()
    flash("KM updated successfully", "success")
    return redirect(url_for("dashboard"))
    

@app.route("/admin/marshalls/add", methods=["POST"])
@admin_required
def add_marshall():
    marshall = request.form.get("marshall", "").strip()
    password = request.form.get("password", "").strip()
    platform_id = request.form.get(platform_id)

    if not marshall or not password or not platform_id:
        flash("All fields are required", "error")
        return redirect(url_for("manage_marshalls"))
    
    conn = get_db()
    cursor = conn.cursor()
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("""
            INSERT INTO users (username, password, role, platform_id)
            VALUES (?, ?, ?, ?)
        """, (marshall, hashed, "marshall", platform_id))

    except sqlite3.IntegrityError:
        flash("Username already taken", "error")
        conn.close()
        return redirect(url_for("manage_marshalls"))
    conn.commit()
    conn.close()
    flash("Marshall created successfully", "success")
    return redirect(url_for("manage_marshalls"))

@app.route("/admin/marshalls", methods=["GET"])
@admin_required
def manage_marshalls():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE role = 'marshall'")
    marshalls = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM platforms")
    platforms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_marshalls_admin.html", marshalls=marshalls, platforms=platforms)

@app.route("/admin/subscriptions", methods=["GET", "POST"])
@login_required
def manage_subscriptions():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        username = request.form.get("username")
        new_paid_until = request.form.get("paid_until")
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if not existing_user:
            flash(f"No user found with username '{username}'", "error")
        else:
            cursor.execute(
                "UPDATE users SET paid_until = ? WHERE username = ?",
                (new_paid_until, username)
            )
            conn.commit()
            flash(f"{username} updated - paid until {new_paid_until}", "success")
    
    cursor.execute("SELECT id, username, role, created_at, paid_until FROM users")
    all_users = cursor.fetchall()

    cursor.execute("SELECT owner_id, driver_username FROM taxis")
    taxi_links = cursor.fetchall()

    owners = []
    for u in all_users:
        if u["role"] == "owner":
            active, days_remaining = check_trial(u["username"])
            owners.append({
                "username": u["username"], "role": u["role"],
                "paid_until": u["paid_until"], "active": active,
                "days_remaining": days_remaining, "drivers": []
            })

    for owner in owners:
        for link in taxi_links:
            for u in all_users:
                if u["id"] == link["owner_id"] and u["username"] == owner["username"]:
                    for driver_row in all_users:
                        if driver_row["username"] == link["driver_username"]:
                            active, days_remaining = check_trial(driver_row["username"])
                            owner["drivers"].append({
                                "username": driver_row["username"],
                                "active": active,
                                "days_remaining": days_remaining,
                                "paid_until": driver_row["paid_until"]
                            })
    
    return render_template("admin_subscriptions.html", owners=owners)

@app.route("/admin/platforms", methods=["GET"])
@admin_required
def manage_platforms():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM platforms")
    platforms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("admin_platforms.html", platforms=platforms)

@app.route("/admin/platforms/add", methods=["POST"])
@admin_required
def add_platform():
    name = request.form.get("name", "").strip()
    rank_name = request.form.get("rank_name", "").strip()

    if not name or not rank_name:
        flash("Platform name and rank name are required", "error")
        return redirect(url_for("manage_platforms"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO platforms (name, rank_name) VALUES (?, ?)",
        (name, rank_name)
    )
    conn.commit()
    conn.close()
    flash(f"Platform '{name}' added", "success")
    return redirect(url_for("manage_platforms"))  

@app.route("/api/queue/join", methods=["POST"])
@login_required
def join_queue():
    if session["role"] != "marshall":
        logger.warning("Non-marshall user=%s attempted to join queue", session["user"])
        return jsonify({"error": "Access denied"}), 403

    taxi_id = request.form.get("taxi_id")
    if not taxi_id:
        flash("Taxi is required", "error")
        return redirect(url_for("marshall"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
    marshall_row = cursor.fetchone()
    platform_id = marshall_row["platform_id"]

    if not platform_id:
        logger.warning("Marshall user=%s has no platform assigned", session["user"])
        conn.close()
        flash("Your marshall account has no platform assigned. Contact admin.", "error")
        return redirect(url_for("marshall"))

    cursor.execute(
        "SELECT COALESCE(MAX(position), 0) as max_pos FROM queue WHERE platform_id = ? AND status = 'waiting'",
        (platform_id,)
    )
    next_position = cursor.fetchone()["max_pos"] + 1

    cursor.execute("""
        INSERT INTO queue (taxi_id, platform_id, position, status)
        VALUES (?, ?, ?, 'waiting')
    """, (taxi_id, platform_id, next_position))  
    conn.commit()
    conn.close()
    flash(f"Taxi added to queue at position {next_position}", "success")
    return redirect(url_for("marshall"))

@app.route("/api/queue", methods=["GET"])
@login_required
def get_queue():
    conn = get_db()
    cursor = conn.cursor()

    if session["role"] == "marshall":
        cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
        platform_id = cursor.fetchone()["platform_id"]
    elif session["role"] == "driver":
        cursor.execute("SELECT platform_id FROM taxis WHERE driver_username = ?", (session["user"],))
        taxi_row = cursor.fetchone()
        platform_id = taxi_row["platform_id"] if taxi_row else None
    else:
        platform_id = request.args.get("platform_id")

    cursor.execute("""
        SELECT q.id, q.position, q.status, t.plate, t.driver_name
        FROM queue q
        JOIN taxis t ON q.taxi_id = t.id
        WHERE q.platform_id = ? AND q.status = 'waiting'
        ORDER BY q.position ASC
    """, (platform_id,))
    queue = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(queue)

@app.route("/api/queue/depart", methods=["POST"])
@login_required
def depart_queue():
    if session["role"] != "marshall":
        logger.warning("Non-marshall user=%s attempted to depart queue", session["user"])
        return jsonify({"error": "Access denied"}), 403

    route_id = request.form.get("route_id")
    if not route_id:
        return jsonify({"error": "Route is required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT platform_id FROM users WHERE username = ?", (session["user"],))
    platform_id = cursor.fetchone()["platform_id"]

    cursor.execute("""
        SELECT id, taxi_id FROM queue WHERE platform_id = ? AND status = 'waiting'
        ORDER BY position ASC LIMIT 1
    """, (platform_id,))
    front = cursor.fetchone()

    if not front:
        logger.info("Marshall user=%s attempted depart on empty queue, platform_id=%s", session["user"], platform_id)
        conn.close()
        return jsonify({"error": "Queue is empty"}), 400

    cursor.execute("""
        INSERT INTO trips (taxi_id, route_id, logged_by)
        VALUES (?, ?, ?)
    """, (front["taxi_id"], route_id, session["user_id"]))

    cursor.execute("UPDATE queue SET status = 'departed' WHERE id = ?", (front["id"],))
    cursor.execute("""
        UPDATE queue SET position = position - 1
        WHERE platform_id = ? AND status = 'waiting'
    """, (platform_id,))

    conn.commit()
    conn.close()
    return jsonify({"message": "Trip logged, position 1 departed, queue shifted"}), 200

@app.route("/admin/platforms/assign", methods=["GET", "POST"])
@admin_required
def assign_platform():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        taxi_id = request.form.get("taxi_id")
        platform_id = request.form.get("platform_id")
        if not taxi_id or not platform_id:
            flash("Taxi and platform are required", "error")
        else:
            cursor.execute("UPDATE taxis SET platform_id = ? WHERE id = ?", (platform_id, taxi_id))
            conn.commit()
            flash("Taxi assigned to platform", "success")

    cursor.execute("SELECT id, plate, driver_name FROM taxis")
    taxis = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM platforms")
    platforms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("admin_assign_platform.html", taxis=taxis, platforms=platforms)

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'owner' AND username != 'sechaba_admin'")
    total_owners = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM taxis")
    total_taxis = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM taxis WHERE platform_id IS NULL")
    unassigned_taxis = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'marshall'")
    total_marshalls = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT p.name, p.rank_name, COUNT(t.id) as taxi_count
        FROM platforms p
        LEFT JOIN taxis t ON t.platform_id = p.id
        GROUP BY p.id
    """)
    platform_summary = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template("admin_dashboard.html",
                           username=session["user"],
                           total_owners=total_owners,
                           total_taxis=total_taxis,
                           unassigned_taxis=unassigned_taxis,
                           total_marshalls=total_marshalls,
                           platform_summary=platform_summary)

def build_taxi_rows(taxis):
    yield ["Plate", "Driver", "Trips", "Collected", "Target"]
    for taxi in taxis:
        yield [taxi["plate"], taxi["driver_name"] or "No driver",
               taxi["trips_today"], f"R{taxi['collected']}", f"R{taxi['target']}"]

@app.route("/reports/daily")
@login_required
def download_daily_report():
    logger.info("User=%s requested daily report", session["user"])
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id
            AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id
            AND dt.date = ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (today, today, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    logger.info("Daily report generated successfully for user=%s, taxis=%d", session["user"], len(taxis))
    return build_pdf_report(taxis, f"Daily Report - {today}", f"separaka_daily_{today}.pdf", build_taxi_rows)

def build_pdf_report(taxis, title, filename, row_builder):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 16)]

    rows = list(row_builder(taxis))
    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

def build_summary_rows(taxis):
    yield ["Plate", "Driver", "Trips", "Collected"]
    for taxi in taxis:
        yield [taxi["plate"], taxi["driver_name"] or "No driver",
               taxi["trips"], f"R{taxi['collected']}"]


@app.route("/reports/weekly")
@login_required
def download_weekly_report():
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.plate, t.driver_name,
                COUNT(tr.id) as trips,
                COALESCE(SUM(dt.collected_amount), 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) >= ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date >= ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (week_ago, week_ago, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return build_pdf_report(taxis, f"Weekly Report ({week_ago} to {today})", f"separaka_weekly_{today}.pdf", build_summary_rows)

@app.route("/reports/monthly")
@login_required
def download_monthly_report():
    month_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.plate, t.driver_name,
                COUNT(tr.id) as trips,
                COALESCE(SUM(dt.collected_amount), 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) >= ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date >= ?
        WHERE t.owner_id = ?
        GROUP BY t.id
    """, (month_ago, month_ago, session["user_id"]))
    taxis = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return build_pdf_report(taxis, f"Monthly Report ({month_ago} to {today})", f"separaka_monthly_{today}.pdf", build_summary_rows)




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
