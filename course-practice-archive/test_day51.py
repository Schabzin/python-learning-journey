import sqlite3
from flask import Flask, redirect, render_template, url_for, request
from flask import flash
import bcrypt

app = Flask(__name__)
app.secret_key = "sechaba2026"

def get_db():
    conn = sqlite3.connect("test_registration.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL)
    """)
    conn.commit()
    return conn

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        print("Submitted:", request.form)
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        errors = []

        if not username:
            errors.append("Username is required")
        if len(username) <3:
            errors.append("Username must at least 3 characters")

        if not password:
            errors.append("Password is required")
        if len(password) <6:
            errors.append("Password must have at least 6 characters")

        if "@" not in email:
            errors.append("Valid email required")

        if errors:
            return render_template("test_register.html",
                errors=errors,
                username=username,
                email=email
            ),400 
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = cursor.fetchone()

        if existing:
            errors.append("Username already taken")
            conn.close()
            return render_template("test_register.html",
                errors=errors,
                username=username,
                email=email), 400
        
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        try:
            cursor.execute("""
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            """, (username, hashed, email))
            conn.commit()
            conn.close()
            flash("Account created successfully", "success")
            return redirect(url_for("register"))
        except sqlite3.IntegrityError:
            errors.append("Email already registered")
            conn.close()
            return render_template("test_register.html",
                errors=errors,
                username=username,
                email=email), 400
    return render_template("test_register.html")
      
if __name__ == "__main__":
    app.run(debug=True)
           