import os
import sqlite3
import datetime
from functools import wraps
from flask import session, redirect, url_for, jsonify

ANCHOR_DATE = datetime.date(2026, 7, 25)
ANCHOR_LETTER = "B"


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

def get_weekend_letter(check_date=None):
    if check_date is None:
        check_date = datetime.date.today()
    days_since_anchor = (check_date - ANCHOR_DATE).days
    weeks_since_anchor = days_since_anchor // 7
    if weeks_since_anchor % 2 == 0:
        return ANCHOR_LETTER
    return "A" if ANCHOR_LETTER == "B" else "B"

def taxi_should_be_working(taxi_weekend_letter):
    if not taxi_weekend_letter:
        return True
    return taxi_weekend_letter == get_weekend_letter()
