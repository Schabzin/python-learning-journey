import sqlite3

DB_PATH = "passenger_counts.db"

def get_connection(db_path=DB_PATH):
    """
    Opens a connection to the trips database with foreign keys enforced.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def calculate_expected_revenue(trip_id, fare_per_passenger, db_path=DB_PATH):
    """
    Calculate expected revenue for a trip -- but only if it's
    a revenue-type leg. Feeder legs return 0 by design.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT route_type FROM trips WHERE trip_id = ?", (trip_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        raise ValueError(f"No trip found with id {trip_id}")

    route_type = result[0]

    if route_type == "feeder":
        conn.close()
        print(f"Trip {trip_id} (feeder): R0 -- free leg, no fare expected.")
        return 0

    cursor.execute("""
        SELECT COUNT(*) FROM crossings
        WHERE trip_id = ? AND direction = 'IN'
    """, (trip_id,))
    passenger_count = cursor.fetchone()[0]

    conn.close()
    expected = passenger_count * fare_per_passenger
    print(f"Trip {trip_id} ({route_type}): {passenger_count} passengers x R{fare_per_passenger} = R{expected}")
    return expected

def flag_trip(trip_id, cash_submitted, fare_per_passenger, db_path=DB_PATH, tolerance=0.10):
    """
    Compares expected revenue (from camera counts) against cash a
    driver actually submitted, and return a discrepancy REPORT --
    never an accusation. tolerance is a percentage (0.10 = 10%)
    allowed before a mismatch is even worth flagging, since drivers
    round change, give small discounts, etc. in the real world.
    """
    expected = calculate_expected_revenue(trip_id, fare_per_passenger, db_path)

    if expected == 0:
        return {
            "trip_id": trip_id,
            "expected": 0,
            "submitted": cash_submitted,
            "status": "Not Applicable",
            "confidence": None,
            "note": "Feeder leg -- no revenue expected on this taxi."
        }

    difference = expected - cash_submitted
    percent_gap = abs(difference) / expected

    if percent_gap <= tolerance:
        status = "Verified"
        confidence = "High"
        note = "Submitted cash matches expected revenue within tolerance."
    elif percent_gap <= tolerance * 3:
        status = "Review"
        confidence = "Medium"
        note = f"R{abs(difference):.2f} gap between expected and submitted -- worth checking, not yet conclusive."
    else:
        status = "Review"
        confidence = "Low"
        note = f"R{abs(difference):.2f} gap is large relative to expected revenue -- flagged for investigation."

    return {
        "trip_id": trip_id,
        "expected": expected,
        "submitted": cash_submitted,
        "difference": difference,
        "status": status,
        "confidence": confidence,
        "note": note
    }

if __name__ == "__main__":
    print(flag_trip(trip_id=12, cash_submitted=75, fare_per_passenger=25))
    print(flag_trip(trip_id=14, cash_submitted=60, fare_per_passenger=25))
    print(flag_trip(trip_id=18, cash_submitted=30, fare_per_passenger=25))
    print(flag_trip(trip_id=19, cash_submitted=0, fare_per_passenger=25))