from flask import Blueprint, request, jsonify
from geofencing import detect_zone_transition, handle_zone_transition


geofencing_bp = Blueprint("geofencing", __name__)

@geofencing_bp.route("/api/taxi/ping", methods=["POST"])
def taxi_ping():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    taxi_id = data.get("taxi_id")
    lat = data.get("lat")
    lon = data.get("lon")

    if taxi_id is None:
        return jsonify({"error": "taxi_id is required"}), 400
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
        transition = detect_zone_transition(taxi_id, lat, lon)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    handle_zone_transition(
        taxi_id=taxi_id,
        event=transition["event"],
        zone_id=transition["zone_id"],
        previous_zone_id=transition["previous_zone_id"],
    )

    return jsonify(transition), 200