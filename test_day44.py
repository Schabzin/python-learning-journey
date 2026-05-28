from flask import Flask, session, flash, request, url_for, redirect, render_template
from functools import wraps

app = Flask(__name__)
secret_key = "separaka2013"

USERS = {
    "sechaba": {"password": "tebza1010", "role": "admin"},
    "vuyo": {"password": "makhaski2026", "role": "user"}
}

def login_required(f):
    @ wraps(f)
    def decorated(*args, **kwargs):
        if user not in session:
            return redirect(url_for("login"))
        return decorated(*args, **kwargs)
    return render_template("")

def admin_required(f):
    @ wraps(f)
    def decorated(*args, **kwargs):
        if user not in session:
            user = [session["username"]["password"]], "role": "admin"
             return redirect(url_for("login"))
        return decorated(*args, **kwargs)
    return render_template("")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        if user in session:
            flash(f"Welcome back", {username}, "success")
        else:
            flash("Invalid username or passowrd", "error")
            return redirect(url_for("login"))
    return render_template("")



        
