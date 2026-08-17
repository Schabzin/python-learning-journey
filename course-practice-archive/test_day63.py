import sqlite3
import time
import datetime
from functools import wraps
from flask import Flask, request, jsonify, session, redirect, url_for, flash, render_template
from taxi_app import app, get_db, admin_required

app = Flask(__name__)

def paid_until():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("ALTER users COLUMN paid_until DATE DEFAULT NULL")
    conn.commit()
    conn.close()

def check_trial(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT created_at, paid_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user["paid_until"]:
        paid_until = datetime.datetime.fromisoformat(user["paid_until"])
        if datetime.datetime.now() < paid_until:
            return True, 999
        else:
            return False,0
        
    if not user["created_at"]:
        return True, 30
    created = datetime.datetime.fromisoformat(user["created_at"])
    days_used = (datetime.datetime.now() - created).days
    days_remaining = 30 - days_used
    return days_remaining > 0, days_remaining

def admin_required(f):
    @wraps(f)
    def decorated(*args, ** kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route("/admin/subscriptions", methods=["GET", "POST"])
@admin_required
def manage_subcription():
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
        
        cursor.execute("SELECT username, role, created_at, paid_until FROM users")
        all_users = cursor.fetchall()
        conn.close()

        users_with_status = []

        for user in all_users:
            active, days_remaining = check_trial(user["username"])
            users_with_status.append({
                "username": user["username"], "role": user["role"],
                "paid_until": user["paid_until"],
                "active":active, "days_remaining": days_remaining
            })
        return render_template("test_day63.html", users=users_with_status)
    
if __name__ == "__main__":
    app.run(debug=True)











    









