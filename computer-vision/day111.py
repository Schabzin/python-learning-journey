import sqlite3
from datetime import datetime, timedelta

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

    trip_start = parse_crossing_time(result[0])

    cursor.execute("""
        SELECT crossing_id, timestamp FROM crossings
        WHERE trip_id = ? AND direction = 'IN'
        ORDER BY timestamp
    """, (trip_id,))
    in_crossings = cursor.fetchall()
    conn.close()

    flagged = []

    for crossing_id, timestamp_str in in_crossings:
        crossing_time = parse_crossing_time(timestamp_str)
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

def analyze_boarding_pattern(trip_id, boarding_window_minutes=10, cluster_window_seconds=90, db_path=DB_PATH):
    """
    Take the flagged mid-route boardings from detect_midroute_boarding()
    and looks at how they're spaced in time. A single late boarding is
    most likely an ordinary roadside pickup. Several boardings clustered
    within a short window of each other is a much stronger signal of a
    coordinated event -- like a highway swap -- since real independent
    roadside pickups don't usually happen seconds apart from each other.

    This still never asserts a swap happened -- it only raises the
    confidence that something coordinated is worth a human's attention.
    """
    flagged_result = detect_midroute_boarding(trip_id, boarding_window_minutes, db_path)
    flagged = flagged_result["flagged_boardings"]

    if len(flagged) == 0:
        return {
            "trip_id": trip_id,
            "pattern": "Single Late Boarding",
            "flagged_count": 1,
            "note": "One passenger boarded late -- consistent with a normal roadside pickup.",
            "clusters": []
        }

    conn = get_connection(db_path)
    cursor = conn.cursor()

    timestamps = []
    for entry in flagged:
        cursor.execute("SELECT timestamp FROM crossings WHERE crossing_id = ?", (entry["crossing_id"],))
        timestamps.append(datetime.strptime(cursor.fetchone()[0], "%H:%M:%S"))
    conn.close()

    timestamps.sort()
    clusters = []
    current_cluster = [timestamps[0]]

    for i in range(1, len(timestamps)):
        gap_seconds = (timestamps[i] - timestamps[i - 1]).total_seconds()
        if gap_seconds <= cluster_window_seconds:
            current_cluster.append(timestamps[i])
        else:
            if len(current_cluster) > 1:
                clusters.append(current_cluster)
            current_cluster = [timestamps[i]]

    if len(current_cluster) > 1:
        clusters.append(current_cluster)

    if clusters:
        pattern = "Clustered Boarding -- Needs Review"
        note = (f"{len(clusters[0])} passengers boarded within "
                f"{cluster_window_seconds} seconds of each other, mid-route -- "
                f"stronger pattern than an ordinary roadside pickup. Not confirmed "
                f"as a swap, but worth a human looking at this specific trip.")

    else:
        pattern = "Multiple Separate Late Boardings"
        note = "More than one late boarding, but spaced apart -- likely independent roadside pickups."

    return {
        "trip_id": trip_id,
        "pattern": pattern,
        "flagged_count": len(flagged),
        "note": note,
        "clusters": clusters
    }

def find_corroborating_swap_evidence(trip_id, cluster_timestamps, corroboration_tolerance_seconds=120, db_path=DB_PATH):
    """
    Given a taxi's clustered IN boarding times, checks whether any OTHER
    taxi logged OUT crossings (people leaving) within a tolerance window
    of that same cluster. Two independent taxis' cameras agreeing something
    happened at the same time is real corroborating evidence -- much
    stronger than one taxi's timing pattern alone. Still never a verdict:
    it raises confidence, it doesn't confirm intent.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT taxi_id FROM trips WHERE trip_id = ?", (trip_id,))
    this_taxi_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT c.crossing_id, t.taxi_id, t.trip_id, c.timestamp
        FROM crossings c
        JOIN trips t ON c.trip_id = t.trip_id
        WHERE c.direction = 'OUT' AND t.taxi_id != ?
    """, (this_taxi_id,))
    other_out_crossings = cursor.fetchall()
    conn.close()

    cluster_times = [parse_crossing_time(ts) for ts in cluster_timestamps]
    window_start = min(cluster_times) - timedelta(seconds=corroboration_tolerance_seconds)
    window_end = max(cluster_times) + timedelta(seconds=corroboration_tolerance_seconds)

    matches = []
    for crossing_id, other_taxi_id, other_trip_id, ts in other_out_crossings:
        crossing_time = parse_crossing_time(ts)
        if window_start <= crossing_time <= window_end:
            matches.append({
                "crossing_id": crossing_id,
                "taxi_id": other_taxi_id,
                "trip_id": other_trip_id,
                "timestamp": ts
            })

    if matches:
        return {
            "status": "Corroborated",
            "matching_taxi_events": matches,
            "note": f"{len(matches)} OUT crossing(s) from other taxi(s) fall within the "
                    f"same time window as this cluster -- real cross-vehicle evidence, "
                    f"still needs a human to confirm what actually happened."
        }
    else:
        return {
            "status": "No Corroboration Found",
            "matching_taxi_events": [],
            "note": "No other taxi logged matching OUT activity in this window -- "
                    "the cluster stands alone, weaker evidence on its own."
        }

def parse_crossing_time(timestamp_str):
    """
    Crossing timestamps in this database exist in two formats depending
    on how they were logged: time-only ('HH:MM:SS', from manual TIME('now')
    test inserts) or full datetime ('YYY-MM-DD HH:MM:SS', from the live
    counter's datetime.now() calls). This normalizes either one down to
    just the time, so every function can compare them on equal footing.
    """
    if " " in timestamp_str:
        timestamp_str = timestamp_str.split(" ")[1]
    timestamp_str = timestamp_str.split(".")[0]
    return datetime.strptime(timestamp_str, "%H:%M:%S")
                                        



if __name__ == "__main__":

    print(detect_midroute_boarding(trip_id=12, boarding_window_minutes=10))
    print(get_connection().execute("SELECT time_started FROM trips WHERE trip_id = 12").fetchone())
    

    conn = get_connection()
    cursor = conn.cursor()
    cluster_times = ["12:30:30", "12:31:00", "12:31:15"]

    for i, ts in enumerate(cluster_times):
        cursor.execute("""
            INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net)
            VALUES (?, ?, 'IN', ?, ?)
        """, (12, ts, 100 + i, 5 + i))
    conn.commit()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trips (taxi_id, date_started, time_started, route_type)
        VALUES (?, DATE('now'), ?, 'revenue')
    """, ("FG09KL GP", "12:20:00"))
    other_trip_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net)
        VALUES (?, ?, 'OUT', ?, ?)
    """, (other_trip_id, "13:15:00", 200, 0))
    conn.commit()
    conn.close()

    print(analyze_boarding_pattern(trip_id=12))
    print(analyze_boarding_pattern(trip_id=14))
    print(analyze_boarding_pattern(trip_id=18))
    print(find_corroborating_swap_evidence(trip_id=12, cluster_timestamps=["12:30:30", "12:31:00", "12:31:15"]))

    