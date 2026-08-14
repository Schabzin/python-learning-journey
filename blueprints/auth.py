from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import bcrypt
import sqlite3
import datetime
import os
import secrets
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from utils import get_db

logger = logging.getLogger(__name__)

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
            return redirect(url_for("owner.dashboard"))
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


def generate_reset_token():
    return secrets.token_urlsafe(32)


def send_email(to_address, subject, body):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.environ.get("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_address}],
        sender={"email": os.environ.get("EMAIL_ADDRESS"), "name": "Separaka"},
        subject=subject,
        text_content=body
    )
    try:
        api_instance.send_transac_email(send_smtp_email)
        logger.info("event=email_sent to=%s", to_address)
    except ApiException as e:
        logger.error("event=email_failed to=%s error=%s", to_address, str(e))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            token = generate_reset_token()
            expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
            cursor.execute("""
                INSERT INTO password_resets (user_id, token, expires_at)
                VALUES (?, ?, ?)
            """, (user["id"], token, expires_at))
            conn.commit()

            reset_link = f"https://separaka.co.za/reset-password/{token}"
            if user["email"]:
                send_email(user["email"], "Reset Your Separaka Password",
                           f"Click here to reset your password: {reset_link}\nThis link expires in 1 hour.")
                logger.info("event=password_reset_requested user=%s", username)
            else:
                logger.warning("event=password_reset_no_email user=%s", username)

        conn.close()
        flash("If that username exists, a reset link has been sent.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM password_resets WHERE token = ?", (token,))
    reset_request = cursor.fetchone()

    if not reset_request:
        conn.close()
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.login"))

    expires_at = datetime.datetime.fromisoformat(reset_request["expires_at"])
    if datetime.datetime.now() > expires_at or reset_request["used"]:
        conn.close()
        logger.warning("event=expired_reset_token_used token=%s", token[:8])
        flash("This reset link has expired or already been used.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("password", "").strip()
        if len(new_password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("reset_password.html", token=token)

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, reset_request["user_id"]))
        cursor.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        logger.info("event=password_reset_completed user_id=%s", reset_request["user_id"])
        flash("Password updated successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    conn.close()
    return render_template("reset_password.html", token=token)