from flask import Flask, request, flash, url_for, redirect
from taxi_app import get_db, owner_required

app = Flask(__name__)

@app.route("/api/km", methods=["POST"])
@owner_required
def update_km():
    taxi_id = request.form.get("taxi_id")
    new_km = request.form.get("current_km")
    if not taxi_id or not new_km:
        flash("Taxi and km reading required", "error")
        return redirect(url_for('dashboard'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE taxis SET current_km = ? WHERE id = ?", (new_km, taxi_id,))
    conn.commit()
    conn.close()
    flash("KM updated successfully", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)


