from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from dotenv import load_dotenv
from functools import wraps
import sqlite3
import bcrypt
import jwt
import datetime
import os
from setup_taxi_db import init_db, create_default_taxis, create_default_users, add_created_at_column, add_platform_support, add_email_column, add_layer_column, add_layers_table, seed_layers, add_phone_column, add_active_column, add_weekend_letter_column, add_prdp_expiry_column
from flask import send_file
import io
import logging
import secrets
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from utils import get_db, login_required, owner_required, admin_required, check_trial, taxi_should_be_working, get_weekend_letter
from blueprints.auth import auth_bp
from blueprints.owner import owner_bp
from blueprints.marshall import marshall_bp
from blueprints.driver import driver_bp
from blueprints.admin import admin_bp
from blueprints.reports import reports_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")

    ]
)
logger = logging.getLogger(__name__)

init_db()
create_default_users()
create_default_taxis()
add_created_at_column()
add_platform_support()
add_email_column()
add_layer_column()
add_phone_column()
add_layers_table()
add_active_column()
seed_layers()
add_weekend_letter_column()
add_prdp_expiry_column()

load_dotenv()

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(owner_bp)
app.register_blueprint(marshall_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(reports_bp)
app.secret_key = os.environ.get("SECRET_KEY", "separaka_taxi_2026")


@app.route("/trial-expired")
@login_required
def trial_expired():
    return render_template("taxi_trial_expired.html", user=session["user"])


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("owner.dashboard"))
    return redirect(url_for("auth.login"))



      
if __name__ == "__main__":
    app.run(debug=True)
