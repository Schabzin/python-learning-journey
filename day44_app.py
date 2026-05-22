from flask import Flask, session, redirect, url_for,request, render_template

app = Flask(__name__)
app.secret_key = "kalikeng2026"

USERS = {
    "sechaba": "kalikeng2026",
    "chahane": "separaka2026"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]
        print(f"Username: '{username}' Password: '{password}'")

        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("day44_login.html", error="Invalid credentials")
        
    return render_template("day44_login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("day44_dashboard.html", user=session["user"])

if __name__ == "__main__":
    app.run(debug=True)
