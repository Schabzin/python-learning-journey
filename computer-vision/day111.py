import sqlite3
from datetime import datetime

DB_PATH = "passenger_counts.db"

def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def detect_midroute_boarding(trip_id, boarding_window_minutes=5, db_path=DB_PATH):
    """
    Flags IN crossings that happened well after a trip's official start
    time -- a signal of possible mid-route boarding (a highway swap,
    or simply a late pickup), NOT a confirmed fraud event. This is a
    detection tool, not a verdict.

    boarding_window_minutes is how long after trip start a boarding
    still counts as "normal rank loading" -- passengers don't all
    climb in at exactly the same second, so a small window is honest,
    not just a strict cutoff.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT time_started FROM trips WHERE trip_id = ?", (trip_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        raise ValueError(f"No trip found with id {trip_id}")

    trip_start = datetime.strptime(result[0], "%H:%M:%S")

    cursor.execute("""
        SELECT crossing_id, timestamp FROM crossings
        WHERE trip_id = ? AND direction = 'IN'
        ORDER BY timestamp
    """, (trip_id,))
    in_crossings = cursor.fetchall()
    conn.close()

    flagged = []

    for crossing_id, timestamp_str in in_crossings:
        crossing_time = datetime.strptime(timestamp_str, "%H:%M:%S")
        minutes_after_start = (crossing_time - trip_start).total_seconds() / 60

        if minutes_after_start > boarding_window_minutes:
            flagged.append({
                "crossing_id": crossing_id,
                "trip_id": trip_id,
                "minutes_after_start": round(minutes_after_start, 1),
                "status": "Needs Review",
                "note": f"Boarding occurred {minutes_after_start:.1f} minutes after trip start -- "
                        f"outside normal rank-loading window. Could be a late pickup or a "
                        f"mid-route boarding event -- needs a human to confirm which."
            })

    return {
        "trip_id": trip_id,
        "total_in_crossings": len(in_crossings),
        "flagged_boardings": flagged,
        "flagged_count": len(flagged)
    }

if __name__ == "__main__":
    print(detect_midroute_boarding(trip_id=12, boarding_window_minutes=10))
    print(get_connection().execute("SELECT time_started FROM trips WHERE trip_id = 12").fetchone())

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net)
        VALUES (?, ?, 'IN', ?, ?)
    """, (12, "12:30:00", 99, 4))
    conn.commit()
    conn.close()

    print(detect_midroute_boarding(trip_id=12, boarding_window_minutes=10))

    