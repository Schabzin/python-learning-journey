import math
import sqlite3

DB_PATH = "passenger_counts.db"

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """
    Return the great-circle distance between two GPS points, in meters.
    Straight-line (Pythagorean) distance is wrong on a sphere -- degrees of
    longitude shrink as you move away from the rquator, so this formula
    accounts for the Earth's curvature instead of treating lat/lon like a
    flat grid.
    """
    EARTH_RADIUS_METERS = 6_371_000

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2
         + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_METERS * c

def is_within_geofence(taxi_lat, taxi_lon, zone_lat, zone_lon, radius_meters):
    """
    True if the taxi's current GPS point falls inside the circular zone
    defined by (zone_lat, zone_lon) and radius_meters.
    """
    distance = haversine_distance_meters(taxi_lat, taxi_lon, zone_lat, zone_lon)
    return distance <= radius_meters

def detect_zone_transition(taxi_id, current_lat, current_lon, db_path=DB_PATH):
    """
    Compares a taxi's current GPS position against its last known geofence
    state and returns what changed, if anything. This is the function that
    would fire trip-start / trip-end logic -- it doesn't fire them itself,
    it just tells the caller what happened.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT last_known_zone_id FROM taxis WHERE id = ?", (taxi_id,)
    )
    row = cursor.fetchone()
    previous_zone_id = row[0] if row else None

    cursor.execute("SELECT id, center_lat, center_lon, radius_meters FROM geofence_zones")
    current_zone_id = None
    for zone_id, zone_lat, zone_lon, radius in cursor.fetchall():
        if is_within_geofence(current_lat, current_lon, zone_lat, zone_lon, radius):
            current_zone_id = zone_id
            break

    cursor.execute(
        "UPDATE taxis SET last_known_zone_id = ? WHERE id = ?",
        (current_zone_id, taxi_id)
    )
    conn.commit()
    conn.close()

    if previous_zone_id == current_zone_id:
        return {"event": "no_change", "zone_id": current_zone_id}
    elif current_zone_id is not None:
        return {"event": "entered_zone", "zone_id": current_zone_id}
    else:
        return {"event": "exited_zone", "zone_id": previous_zone_id}