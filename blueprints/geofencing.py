from flask import Blueprint, request, jsonify, current_app, session
from geofencing import detect_zone_transition, handle_zone_transition
from gps_history import parse_recorded_at, parse_accuracy, save_ping, PingError
import sqlite3
from utils import get_db_path


geofencing_bp = Blueprint("geofencing", __name__)

def _taxi_id_for_logged_in_driver():
    """The taxi assigned to the logged-in driver, or None."""
    conn = sqlite3.connect(get_db_path())
    try:
        row = conn.ex(
            "SELECT id FROM taxis WHERE driver_username = ?",
            (session["user"],),
        ).fetchone()
    finally:
        conn.close()
    return row[0] if  row else None

@geofencing_bp.route("/api/taxi/ping", methods=["POST"])
def taxi_ping():
    if "user" not in session:
        return jsonify({"error": "Login required"}), 401
    if session.get("role") != "driver":
        return jsonify({"error": "Only drivers can send pings"}), 403

    taxi_id = _taxi_id_for_logged_in_driver()
    if taxi_id is None:
        return jsonify({"error": "No taxi assigned to this driver"}), 403

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    lat = data.get("lat")
    lon = data.get("lon")

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon are required"}), 400

    
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lon must be numbers"}), 400

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return jsonify({"error": "lat/lon out of valid range"}), 400

    try:
        recorded_at = parse_recorded_at(data.get("recorded_at"))
        accuracy_m = parse_accuracy(data.get("accuracy_m"))
    except PingError as e:
        return jsonify({"error": str(e)}), 400

    try:
        transition = detect_zone_transition(taxi_id, lat, lon)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    try:
        save_ping(taxi_id, lat, lon, recorded_at, accuracy_m)
    except Exception:
        current_app.logger.exception("Could not save GPS ping for taxi %s", taxi_id)

    handle_zone_transition(
        taxi_id=taxi_id,
        event=transition["event"],
        zone_id=transition["zone_id"],
        previous_zone_id=transition["previous_zone_id"],
    )

    return jsonify(transition), 200