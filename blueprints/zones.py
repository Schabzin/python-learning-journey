from flask import Blueprint, request, jsonify
from utils import get_db_path
import sqlite3

zones_bp = Blueprint("zones", __name__)

@zones_bp.route("/api/zones", methods=["POST"])
def create_zone():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get("name")
    zone_type = data.get("zone_type")
    center_lat = data.get("center_lat")
    center_lon = data.get("center_lon")
    radius_meters = data.get("radius_meters")
    route_id = data.get("route_id")

    if not name:
        return jsonify({"error": "name is required"}), 400
    if zone_type not in ("rank", "destination"):
        return jsonify({"error": "zone_type must be 'rank' or 'destination'"})
    if center_lat is None or center_lon is None or radius_meters is None:
        return jsonify({"error": "center_lat, center_lon, and radius_meters are required"}), 400

    try:
        center_lat = float(center_lat)
        center_lon = float(center_lon)
        radius_meters = float(radius_meters)
    except (TypeError, ValueError):
        return jsonify({"error": "center_lat, center_lon, and radius_meters must be numbers"}), 400

    if not (-90 <= center_lat <= 90) or not (-180 <= center_lon <= 180):
        return jsonify({"error": "center_lat/center_lon out of valid range"}), 400
    if radius_meters <= 0:
        return jsonify({"error": "radius_meters must be greater than 0"}), 400

    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO geofence_zones (name, zone_type, center_lat, center_lon, radius_meters, route_id, active) "
            "VALUES (?, ?, ?, ?, ?, ?, 1)",
            (name, zone_type, center_lat, center_lon, radius_meters, route_id)
        )
        conn.commit()
        new_zone_id = cursor.lastrowid
    finally:
        conn.close()

    return jsonify({"id": new_zone_id, "name": name, "zone_type": zone_type}), 201
    

@zones_bp.route("/api/zones", methods=["GET"])
def list_zones():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor= conn.cursor()
    cursor.execute("SELECT id, namr, center_lat, center_lon, radius_meters FROM geofence_zones WHERE active = 1")
    zones = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(zones), 200

@zones_bp.route("/api/zones/<int:zone_id>", methods=["DELETE"])
def deactivate_zone(zone_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM trips WHERE zone_id = ? AND end_time IS NULL",
        (zone_id,)
    )
    open_trip_count = cursor.fetchone()[0]
    if open_trip_count > 0:
        conn.close()
        return jsonify({"error": "Cannot deactivate a zone with an open trip"}), 409

    cursor.execute("UPDATE geofence_zones SET active = 0 WHERE id = ?", (zone_id,))
    conn.commit()
    conn.close()

    return jsonify({"id": zone_id, "active": False}), 200

