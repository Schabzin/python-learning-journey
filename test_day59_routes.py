from flask import Flask, request, render_template, redirect, url_for, owner_required, get_db, flash
import sqlite3

app = Flask(__name__)

@app.route("/admin/routes", methods=["GET"])
@owner_required
def manage_routes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes (name) VALUE (?)", (routes,))
    routes = [dict(row) for row in cursor.fecthall()]
    conn.commit()
    flash("Route name required", "error")
    return redirect(url_for("manage_routes"))

@app.route("/admin/routes/add", methods=["POST"])
@owner_required
def add_routes():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Route name is required", "error")
        return redirect(url_for("mange_route"))
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT FROM route WHERE id = ?", route=route)
        conn.close()
        flash("Route successfully added", "success")
    except sqlite3.IntegrityError:
        flash("Route already exist", "error")
        return redirect(url_for("manage_route"))
    
@app.route("/admin/routes/delete/<int:route_id>", methods=["POST"])
@owner_required
def delete_routes(route_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM route WHERE name = ?", (name,))
    conn.commit()
    flash("Route deleted successfully", "success")
    conn.close()

if __name__ == (__main__):
    debug=(True)



