from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import bcrypt
import sqlite3
from utils import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower().strip()
        password = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user["active"] == 0:
            flash("This account has been deactivated. Contact your owner.", "error")
            return redirect(url_for("auth.login"))

        if user and bcrypt.checkpw(password.encode(), user["password"]):
            session["user"] = username
            session["role"] = user["role"]
            session["user_id"] = user["id"]
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "error")
        return redirect(url_for("auth.login"))
    return render_template("taxi_login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()

        errors = []
        if not username:
            errors.append("Username is required")
        if len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if not password:
            errors.append("Password is required")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters")
        if not email:
            errors.append("Email is required")
        elif "@" not in email or "." not in email:
            errors.append("Please enter a valid email address")
        if not phone:
            errors.append("Phone number is required")

        if errors:
            return render_template("taxi_register.html", errors=errors)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return render_template("taxi_register.html", errors=["Username already taken"])

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, email, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (username, hashed, "owner", email, phone))
            conn.commit()
            conn.close()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("auth.login"))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("taxi_register.html", errors=["Username already taken"])

    return render_template("taxi_register.html")