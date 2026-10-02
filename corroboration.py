import sqlite3
from datetime import datetime, timedelta
from utils import get_db_path

CORROBORATION_TOLERANCE_SECONDS = 120

def parse_crossing_time(timestamp_str):
    """
    Crossing timestamps exist in two shapes depending on how they were
    logged: time-only ('HH:MM:SS', from manual test inserts) or full
    datetime('YYYY-MM-DD HH:MM:SS', from the live counter's CURRENT_TIMESTAMP
    default). Normalizes either down to time-only so every comparison
    runs on equal footing. Carried over from Day 111, unchanged logic.
    """
    if " " in timestamp_str:
        timestamp_str = timestamp_str.split(" ")[1]
    timestamp_str = timestamp_str.split(".")[0]
    return datetime.strptime(timestamp_str, "%H:%M:%S")

def find_corroborating_cross_taxi_event(
    trip_id, direction, event_timestamps,
    corroboration_tolerance_seconds=CORROBORATION_TOLERANCE_SECONDS,
    db_path=None
):
    """
    Checks whether a DIFFERENT taxi logged the OPPOSITE crossing direction
    within a tolerance window of this taxi's own event timestamps.

    direction is the direction THIS taxi's events are ('IN' or 'OUT').
    An OUT on this taxi corroborates against an IN somewhere else
    (evidence of a transfer OUT); an IN on this taxi corroborates
    against an OUT somewhere else (evidence of a transfer IN) -- same
    two-sided check Day 111 built, generalized to run either direction.

    Still never a verdict -- raises confidence, never confirms intent.
    """
    if direction not in ("IN", "OUT"):
        raise ValueError(f"direction must be 'IN' or 'OUT', got {direction!r}")
    opposite_direction = "IN" if direction == "OUT" else "OUT"

    conn = sqlite3.connect(db_path or get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT taxi_id FROM trips WHERE id = ?", (trip_id,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError(f"No trip found with id {trip_id}")
        this_taxi_id = row[0]

        cursor.execute("""
            SELECT c.id, t.taxi_id, t.id, c.timestamp
            FROM crossings c
            JOIN trips t ON c.trip_id = t.id
            WHERE c.direction = ? AND t.taxi_id != ?
        """, (opposite_direction, this_taxi_id))
        other_crossings = cursor.fetchall()
    finally:
        conn.close()

    event_times = [parse_crossing_time(ts) for ts in event_timestamps]
    window_start = min(event_times) - timedelta(seconds=corroboration_tolerance_seconds)
    window_end = max(event_times) + timedelta(seconds=corroboration_tolerance_seconds)

    matches = []
    for crossing_id, other_taxi_id, other_trip_id, ts in other_crossings:
        crossing_time = parse_crossing_time(ts)
        if window_start <= crossing_time <= window_end:
            matches.append({
                "crossing_id": crossing_id,
                "taxi_id": other_taxi_id,
                "trip_id": other_trip_id,
                "timestamp": ts,
            })

    if matches:
        return {
            "status": "Corroborated",
            "matching_taxi_events": matches,
            "note": f"{len(matches)} {opposite_direction} crossing(s) from other taxi(s) "
                    f"fall within the same time window -- real cross-vehicle evidence, "
                    f"still needs a human to confirm what actually happened.",
        }
    else:
        return {
            "status": "No Corroboration Found",
            "matching_taxi_events": [],
            "note": "No other taxi logged matching activity in this window -- "
                    "this event stands alone, weaker evidence on its own.",
        }