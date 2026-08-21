from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import bcrypt
import sqlite3
from utils import get_db, admin_required, check_trial, login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
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


@admin_bp.route("/admin/marshalls/add", methods=["POST"])
@admin_required
def add_marshall():
    marshall = request.form.get("marshall", "").strip()
    password = request.form.get("password", "").strip()
    platform_id = request.form.get("platform_id")

    if not marshall or not password or not platform_id:
        flash("All fields are required", "error")
        return redirect(url_for("admin.manage_marshalls"))

    conn = get_db()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role, platform_id) VALUES (?, ?, ?, ?)",
                       (marshall, hashed, "marshall", platform_id))
    except sqlite3.IntegrityError:
        flash("Username already taken", "error")
        conn.close()
        return redirect(url_for("admin.manage_marshalls"))
    conn.commit()
    conn.close()
    flash("Marshall created successfully", "success")
    return redirect(url_for("admin.manage_marshalls"))


@admin_bp.route("/admin/marshalls", methods=["GET"])
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


@admin_bp.route("/admin/subscriptions", methods=["GET", "POST"])
@admin_required
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
            cursor.execute("UPDATE users SET paid_until = ? WHERE username = ?", (new_paid_until, username))
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


@admin_bp.route("/admin/platforms", methods=["GET"])
@admin_required
def manage_platforms():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM platforms")
    platforms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("admin_platforms.html", platforms=platforms)


@admin_bp.route("/admin/platforms/add", methods=["POST"])
@admin_required
def add_platform():
    name = request.form.get("name", "").strip()
    rank_name = request.form.get("rank_name", "").strip()

    if not name or not rank_name:
        flash("Platform name and rank name are required", "error")
        return redirect(url_for("admin.manage_platforms"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO platforms (name, rank_name) VALUES (?, ?)", (name, rank_name))
    conn.commit()
    conn.close()
    flash(f"Platform '{name}' added", "success")
    return redirect(url_for("admin.manage_platforms"))


@admin_bp.route("/admin/platforms/assign", methods=["GET", "POST"])
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


@admin_bp.route("/admin/routes", methods=["GET"])
@admin_required
def manage_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    routes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("taxi_routes_admin.html", routes=routes)


@admin_bp.route("/admin/routes/add", methods=["POST"])
@admin_required
def add_route():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Route name is required", "error")
        return redirect(url_for("admin.manage_routes"))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO routes (name) VALUES (?)", (name,))
        conn.commit()
        flash(f"Route '{name}' added", "success")
    except sqlite3.IntegrityError:
        flash("Route already exists", "error")
    conn.close()
    return redirect(url_for("admin.manage_routes"))


@admin_bp.route("/admin/routes/delete/<int:route_id>", methods=["POST"])
@admin_required
def delete_route(route_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routes WHERE id = ?", (route_id,))
    conn.commit()
    conn.close()
    flash("Route deleted", "success")
    return redirect(url_for("admin.manage_routes"))
    