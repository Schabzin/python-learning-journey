from flask import Flask, session, redirect, url_for,request, render_template
from flask import flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "kalikeng2026"

USERS = {
    "sechaba": {"password": "kalikeng2026", "role": "admin"},
    "chahane": {"password": "separaka2026", "role": "user"}
}

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if USERS[session["user"]]["role"] != "admin":
            return "Access denied", 403
        return f(*args, **kwargs)
    return decorated

@app.route("/admin")
@admin_required
def admin():
    return "Admin panel"

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
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))
    return render_template("day44_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/clients")
@login_required
def clients():
    return "Clients page"

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("day44_dashboard.html", user=session["user"])


if __name__ == "__main__":
    app.run(debug=True)
