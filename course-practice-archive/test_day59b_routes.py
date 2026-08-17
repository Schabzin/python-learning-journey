from flask import Flask, request, url_for, flash, render_template, redirect
from taxi_app import get_db, owner_required
import sqlite3

app = Flask(__name__)

@app.route("/admin/routes", methods=["GET"])
@owner_required
def manage_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT FROM routes")
    routes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    flash("Please select route", "error")
    return render_template(test_day59b.html, routes=routes)

@app.route("/admin/route/add", methods=["POST"])
@owner_required
def add_route():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please add name", "error")
        return redirect(url_for("manage_routes"))
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO route (name) VALUES (?)", (name,))
        conn.commit()
        flash("Route {name} added successfully", "success")
        return redirect(url_for("manage_route"))
    except sqlite3.IntegrityError:
        flash("Route name already exist", "error")

@app.route("/admin/route/delete/<int:route_id>", methods=["POST"])
@owner_required
def delete_route(route_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routes WHERE id = ?", (route_id,))
    conn.commit()
    flash("Route deleted", "success")
    conn.close()
    return redirect(url_for("manage_routes"))

@app.route('/login')
def login():
    return "login placeholder"

if __name__ == "__main__":
    app.run(debug=True)

