from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import bcrypt
import sqlite3
import datetime
import logging
from utils import get_db, login_required, owner_required, check_trial, taxi_should_be_working, prdp_expiring_soon

logger = logging.getLogger(__name__)
owner_bp = Blueprint("owner", __name__)


@owner_bp.route("/dashboard")
@login_required
def dashboard():
    if session["role"] == "marshall":
        return redirect(url_for("marshall.marshall"))
    if session["role"] == "driver":
        return redirect(url_for("driver.driver_dashboard"))
    if session["user"] == "sechaba_admin":
        return redirect(url_for("admin.admin_dashboard"))

    trial_active, days_remaining = check_trial(session["user"])
    if not trial_active:
        return redirect(url_for("trial_expired"))

    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    month_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.driver_name, t.status, t.current_km, t.next_service_km, t.prdp_expiry,
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
        taxi["active_this_weekend"] = taxi_should_be_working(taxi.get("weekend_letter"))

        if prdp_expiring_soon(taxi.get("prdp_expiry")):
            taxi["prdp_warning"] = f"PrDP expires {taxi['prdp_expiry']} - renew soon"
        elif taxi.get("prdp_expiry") and datetime.datetime.strptime(taxi["prdp_expiry"], "%Y-%m-%d").date() < datetime.date.today():
            taxi["prdp_warning"] = f"PrDP EXPIRED on {taxi['prdp_expiry']} - this is urgent"

        print("DEBUG:", taxi["plate"], "prdp_expiry=", taxi.get("prdp_expiry"), "prdp_warning", taxi.get("prdp_warning"), flush=True)

    conn.close()
    return render_template("taxi_dashboard.html",
                           username=session["user"],
                           role=session["role"],
                           taxis=taxis,
                           today=today,
                           days_remaining=days_remaining,
                           week_data=week_data,
                           month_data=month_data)


@owner_bp.route("/api/target", methods=["POST"])
@login_required
def daily_target():
    amount = request.form.get("number")
    taxi_id = request.form.get("taxi_id")

    if not taxi_id or not amount:
        flash("Taxi and target amount are required", "error")
        return redirect(url_for("owner.dashboard"))

    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM daily_targets WHERE taxi_id = ? AND date = ?", (taxi_id, today))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE daily_targets SET target_amount = ? WHERE taxi_id = ? AND date = ?",
                       (float(amount), taxi_id, today))
    else:
        cursor.execute("INSERT INTO daily_targets (taxi_id, date, target_amount) VALUES (?, ?, ?)",
                       (taxi_id, today, float(amount)))

    conn.commit()
    conn.close()
    flash("Target updated successfully", "success")
    return redirect(url_for("owner.dashboard"))


@owner_bp.route("/api/km", methods=["POST"])
@owner_required
def update_km():
    taxi_id = request.form.get("taxi_id")
    new_km = request.form.get("current_km")
    manual_next_service = request.form.get("next_service_km", "").strip()

    if not taxi_id or not new_km:
        flash("Taxi and KM reading required", "error")
        return redirect(url_for("owner.dashboard"))

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

    cursor.execute("UPDATE taxis SET current_km = ?, next_service_km = ? WHERE id = ?",
                   (new_km, new_next_service, taxi_id))
    conn.commit()
    conn.close()
    flash("KM updated successfully", "success")
    return redirect(url_for("owner.dashboard"))


@owner_bp.route("/admin/taxis", methods=["GET"])
@owner_required
def manage_taxis():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, u.active as driver_active
        FROM taxis t
        LEFT JOIN users u ON t.driver_username = u.username
        WHERE t.owner_id = ?
    """, (session["user_id"],))
    taxis = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM platforms")
    platforms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_admin_taxis.html", taxis=taxis, platforms=platforms)


@owner_bp.route("/admin/taxi/add", methods=["POST"])
@owner_required
def add_taxi():
    plate = request.form.get("plate", "").strip()
    driver_name = request.form.get("driver_name", "").strip()
    driver_username = request.form.get("driver_username", "").strip().lower()
    password = request.form.get("password", "").strip()
    platform_id = request.form.get("platform_id")
    weekend_letter = request.form.get("weekend_letter") or None

    if not plate or not driver_name or not driver_username or not password or not platform_id:
        flash("All fields are required", "error")
        return redirect(url_for("owner.manage_taxis"))

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO taxis (plate, driver_name, driver_username, owner_id, platform_id, weekend_letter)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (plate, driver_name, driver_username, session["user_id"], platform_id, weekend_letter))
    except sqlite3.IntegrityError:
        logger.warning("event=duplicate_plate user=%s plate=%s", session["user"], plate)
        flash("Taxi plate already exists", "error")
        conn.close()
        return redirect(url_for("owner.manage_taxis"))

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (driver_username, hashed, "driver"))
    except sqlite3.IntegrityError:
        logger.warning("event=duplicate_plate user=%s plate=%s", session["user"], plate)
        flash("Username already taken", "error")
        conn.close()
        return redirect(url_for("owner.manage_taxis"))
    conn.commit()
    conn.close()
    return redirect(url_for("owner.manage_taxis"))


@owner_bp.route("/admin/taxi/<int:taxi_id>/reassign-driver", methods=["POST"])
@owner_required
def reassign_driver(taxi_id):
    new_driver_name = request.form.get("driver_name", "").strip()
    new_driver_username = request.form.get("driver_username", "").strip()
    new_password = request.form.get("password", "").strip()

    if not new_driver_name or not new_driver_username or not new_password:
        flash("All fields are required", "error")
        return redirect(url_for("owner.manage_taxis"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxis WHERE id = ? AND owner_id = ?", (taxi_id, session["user_id"]))
    taxi = cursor.fetchone()
    if not taxi:
        conn.close()
        flash("Taxi not found", "error")
        return redirect(url_for("owner.manage_taxis"))

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (new_driver_username, hashed, "driver"))
    except sqlite3.IntegrityError:
        flash("Username already taken", "error")
        conn.close()
        return redirect(url_for("owner.manage_taxis"))

    old_driver_username = taxi["driver_username"]
    cursor.execute("UPDATE taxis SET driver_name = ?, driver_username = ? WHERE id = ?",
                   (new_driver_name, new_driver_username, taxi_id))

    if old_driver_username:
        cursor.execute("UPDATE users SET active = 0 WHERE username = ?", (old_driver_username,))

    conn.commit()
    conn.close()
    flash("Driver reassigned successfully", "success")
    return redirect(url_for("owner.manage_taxis"))


@owner_bp.route("/admin/taxi/<int:taxi_id>/update-letter", methods=["POST"])
@owner_required
def update_weekend_letter(taxi_id):
    letter = request.form.get("weekend_letter")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE taxis SET weekend_letter = ? WHERE id = ? AND owner_id = ?",
                   (letter, taxi_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Weekend letter updated", "success")
    return redirect(url_for("owner.manage_taxis"))


@owner_bp.route("/admin/taxi/<int:taxi_id>/reset-driver-password", methods=["POST"])
@owner_required
def reset_driver_password(taxi_id):
    new_password = request.form.get("password", "").strip()
    if not new_password or len(new_password) < 6:
        flash("Password must be at least 6 characters", "error")
        return redirect(url_for("owner.manage_taxis"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxis WHERE id = ? AND owner_id = ?", (taxi_id, session["user_id"]))
    taxi = cursor.fetchone()
    if not taxi or not taxi["driver_username"]:
        conn.close()
        flash("Taxi or driver not found", "error")
        return redirect(url_for("owner.manage_taxis"))

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, taxi["driver_username"]))
    conn.commit()
    conn.close()
    flash("Driver's password has been reset", "success")
    return redirect(url_for("owner.manage_taxis"))

@owner_bp.route("/admin/taxi/<int:taxi_id>/update-prdp", methods=["POST"])
@owner_required
def update_prdp_expiry(taxi_id):
    expiry_date = request.form.get("prdp_expiry")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE taxis SET prdp_expiry = ? WHERE id = ? AND owner_id = ?",
                   (expiry_date, taxi_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("PrDP expiry date updated", "success")
    return redirect(url_for("owner.manage_taxis"))

