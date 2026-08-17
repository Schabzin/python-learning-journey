from flask import Flask, session, flash, request, url_for, redirect, render_template
from functools import wraps

app = Flask(__name__)
app.secret_key = "separaka2013"

USERS = {
    "sechaba": {"password": "tebza1010", "role": "admin"},
    "vuyo": {"password": "makhaski2026", "role": "user"}
}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
             return redirect(url_for("login"))
        if USERS[session["user"]]["role"] != "admin":
            return "Access denied", 403
        return f(*args, **kwargs)
    return decorated
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        if username in USERS and USERS[username]["password"] == password:
            session["user"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or passowrd", "error")
            return redirect(url_for("login"))
    return render_template("test_day44.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("test_day44_dashboard.html", user=session["user"])


@app.route("/admin")
@admin_required
def admin():
    return "Admin panel"

if __name__ == "__main__":
    app.run(debug=True)
        
