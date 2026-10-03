import math
import sqlite3
from datetime import datetime, timedelta
from utils import get_db_path

DB_PATH = get_db_path()
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
    """
    Determine whether a taxi has moved between geofence zones since its last ping.

    Returns:
      - event: "no_change" | "entered_zone" | "exited_zone" | "changed_zone"
      - zone_id: the newly confirmed zone (None if taxi is now outside every zone)
      - previous_zone_id: the zone that was confirmed before this ping (None if
        it wasn't in any zone) -- this is what lets the trip-record layer close
        the old zone's trip and open a new one in the same call.

    Uses a debounce (REQUIRED_CONFIRMATIONS consecutive pings agreeing on the
    same observed zone) before committing to a transition, so one noisy GPS
    reading near a boundry can't flip the taxi's state back and forth.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT last_known_zone_id, pending_zone_id, pending_zone_count "
            "FROM taxis WHERE id = ?", (taxi_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"No taxi registered with id {taxi_id}")

        confirmed_zone_id, pending_zone_id, pending_zone_count = row

        cursor.execute(
            "SELECT id, center_lat, center_lon, radius_meters "
            "FROM geofence_zones WHERE active = 1 ORDER BY radius_meters ASC"
        )
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

        previous_zone_id = confirmed_zone_id
        event = "no_change"

        if pending_zone_count >= REQUIRED_CONFIRMATIONS and pending_zone_id != confirmed_zone_id:
            confirmed_zone_id = pending_zone_id
            pending_zone_count = REQUIRED_CONFIRMATIONS

            if previous_zone_id is None and confirmed_zone_id is not None:
                event = "entered_zone"
            elif previous_zone_id is not None and confirmed_zone_id is None:
                event = "exited_zone"
            else:
                event = "changed_zone"

        cursor.execute(
            "UPDATE taxis SET last_known_zone_id = ?, pending_zone_id = ?, "
            "pending_zone_count = ?, last_ping_at = ? WHERE id = ?",
            (confirmed_zone_id, pending_zone_id, pending_zone_count,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), taxi_id)
        )
        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "event": event,
        "zone_id": confirmed_zone_id,
        "previous_zone_id": previous_zone_id,
    }

def handle_zone_transition(taxi_id, event, zone_id, previous_zone_id, db_path=DB_PATH):
    """
    Turns a detect_zone_transition() result into actual trip records.

    entered_zone   -> open a new trip in zone_id
    exited-zone    -> close the open trip in previous_zone_id
    changed_zone   -> close the trip in previous_zone_id AND open one in zone_id
    no_change      -> nothing to do
    """
    if event == "no_change":
        return None

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if event in ("exited_zone", "changed_zone"):
            cursor.execute(
                "UPDATE zone_occupancy SET end_time = ? "
                "WHERE taxi_id = ? AND zone_id = ? AND end_time IS NULL",
                (now, taxi_id, previous_zone_id)
            )

        if event in ("entered_zone", "changed_zone"):
            cursor.execute(
                "INSERT INTO zone_occupancy (taxi_id, zone_id, start_time, end_time) "
                "VALUES (?, ?, ?, NULL)",
                (taxi_id, zone_id, now)
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def start_trip_from_current_zone(taxi_id, logged_by, db_path=None):
    conn = sqlite3.connect(db_path or get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT zo.zone_id, gz.zone_type, gz.route_id
            FROM zone_occupancy zo
            JOIN geofence_zones gz ON zo.zone_id = gz.id
            WHERE zo.taxi_id = ? AND zo.end_time IS NULL
        """, (taxi_id,))
        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                f"Taxi {taxi_id} is not currently inside any known zone -- "
                "cannot start a trip without knowing where it is."
            )

        zone_id, zone_type, route_id = row

        if route_id is None:
            raise ValueError(
                f"Zone {zone_id} has no route_id set -- "
                "cannot derive route_type without a route."
            )

        if zone_type == "rank":
            route_type = "revenue"
        elif zone_type == "destination":
            route_type = "feeder"
        else:
            raise ValueError(
                f"Taxi {taxi_id} is in zone {zone_id}, a '{zone_type}' zone. "
                "A trip cannot be started from a checkpoint -- checkpoints only mark "
                "progress along a route that has already started."
            )

        cursor.execute("""
            INSERT INTO trips (taxi_id, route_id, route_type, logged_by, timestamp)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (taxi_id, route_id, route_type, logged_by))
        conn.commit()

        return cursor.lastrowid
    finally:
        conn.close()

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
