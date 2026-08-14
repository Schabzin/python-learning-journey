from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
import datetime
from utils import get_db, login_required

driver_bp = Blueprint("driver", __name__)


@driver_bp.route("/driver")
@login_required
def driver_dashboard():
    if session["role"] != "driver":
        return redirect(url_for("owner.dashboard"))

    today = datetime.date.today().isoformat()
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    month_ago = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.plate, t.driver_name, t.status,
                COUNT(tr.id) as trips_today,
                COALESCE(dt.target_amount, 750) as target,
                COALESCE(dt.collected_amount, 0) as collected
        FROM taxis t
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date = ?
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


@driver_bp.route("/api/deposit", methods=["POST"])
@login_required
def log_deposit():
    amount = request.form.get("number")
    if not amount:
        flash("Please enter a deposit amount", "error")
        return redirect(url_for("driver.driver_dashboard"))

    today = datetime.date.today().isoformat()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM taxis WHERE driver_username = ?", (session["user"],))
    taxi = cursor.fetchone()

    if taxi:
        cursor.execute("SELECT id FROM daily_targets WHERE taxi_id = ? AND date = ?", (taxi["id"], today))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE daily_targets SET collected_amount = collected_amount + ?
                WHERE taxi_id = ? AND date = ?
            """, (float(amount), taxi["id"], today))
        else:
            cursor.execute("INSERT INTO daily_targets (taxi_id, date, collected_amount) VALUES (?, ?, ?)",
                           (taxi["id"], today, float(amount)))
        conn.commit()
        conn.close()
        flash("Deposit logged successfully", "success")
        return redirect(url_for("driver.driver_dashboard"))
    else:
        conn.close()
        flash("No taxi found for your account", "error")
        return redirect(url_for("driver.driver_dashboard"))


@driver_bp.route("/api/driver/taxi", methods=["GET"])
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
        LEFT JOIN trips tr ON t.id = tr.taxi_id AND DATE(tr.timestamp) = ?
        LEFT JOIN daily_targets dt ON t.id = dt.taxi_id AND dt.date = ?
        WHERE t.driver_name = ?
        GROUP BY t.id
    """, (today, today, session["user"]))

    taxi = cursor.fetchone()
    conn.close()

    if not taxi:
        return jsonify({"error": "No taxi found"}), 404

    return jsonify(dict(taxi)), 200