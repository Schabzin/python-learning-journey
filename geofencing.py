import math
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "passenger_counts.db"
REQUIRED_CONFIRMATIONS = 2

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
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT last_known_zone_id, pending_zone_id, pending_zone_count "
        "FROM taxis WHERE id = ?", (taxi_id,)
    )
    row = cursor.fetchone()
    confirmed_zone_id, pending_zone_id, pending_zone_count = row if row else (None, None, 0)

    cursor.execute("SELECT id, center_lat, center_lon, radius_meters FROM geofence_zones")
    observed_zone_id = None
    for zone_id, zone_lat, zone_lon, radius in cursor.fetchall():
        if is_within_geofence(current_lat, current_lon, zone_lat, zone_lon, radius):
            observed_zone_id = zone_id
            break

    if observed_zone_id == pending_zone_id:
        pending_zone_count += 1

    else:
        pending_zone_id = observed_zone_id
        pending_zone_count = 1

    event = "no_change"
    if pending_zone_count >= REQUIRED_CONFIRMATIONS and pending_zone_id != confirmed_zone_id:
        previous_confirmed = confirmed_zone_id
        confirmed_zone_id = pending_zone_id
        event = "entered_zone" if confirmed_zone_id is not None else "exited_zone"

    cursor.execute(
        "UPDATE taxis SET last_known_zone_id = ?, pending_zone_id = ?, "
        "pending_zone_count = ?, last_ping_at = ? WHERE id = ?",
        (confirmed_zone_id, pending_zone_id, pending_zone_count,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"), taxi_id)
    )
    conn.commit()
    conn.close()

    return {"event": event, "zone_id": confirmed_zone_id}

def find_stale_active_trips(staleness_minutes=15, db_path=DB_PATH):
    """
    Flags taxis that are confirmed inside a zone (a trip is logically open)
    but haven't sent a GPS ping in a while -- doesn't guess when the trip
    actually ended, just surfaces it for a human to check, the same
    honest-flag-not-verdict pattern as every swap-detection function
    from Day 111.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cutoff = datetime.now() - timedelta(minutes=staleness_minutes)
    cursor.execute("""
        SELECT id, plate, last_known_zone_id, last_ping_at
        FROM taxis
        WHERE last_known_zone_id IS NOT NULL
            AND last_ping_at < ?
    """, (cutoff.strftime("%Y-%m-%d %H:%M:%S"),))

    stale = [
        {"taxi_id": row[0], "plate": row[1], "zone_id": row[2], "last_ping_at": row[3]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return stale
