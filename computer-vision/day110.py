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

def generate_flag_report(taxi_id, cash_submissions, fare_per_passenger, db_path=DB_PATH):
    """
    Runs flag_trip() across every revenue trip a taxi ran, splitting
    results into four groups instead of three: verified, needs_review,
    not_applicable (feeder legs), and no_submission -- trips where the
    driver never submitted a cash figure at all. That last group is
    its own category because "never submitted" is a different, more
    serious signal than "submitted less than expected" -- it isn't
    a discrepancy in the money, it's a missing report entirely.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT trip_id FROM trips WHERE taxi_id = ?
    """, (taxi_id,))
    trip_ids = [row[0] for row in cursor.fetchall()]
    conn.close()

    verified = []
    needs_review = []
    not_applicable = []
    no_submission = []

    for trip_id in trip_ids:
        if trip_id not in cash_submissions:
            conn = get_connection(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT route_type FROM trips WHERE trip_id = ?", (trip_id,))
            route_type = cursor.fetchone()[0]
            conn.close()

            if route_type == "feeder":
                continue

            no_submission.append({
                "trip_id": trip_id,
                "status": "No Submission",
                "confidence": "Low",
                "note": "No cash figure was ever submitted for this revenue trip -- needs follow-up."
            })
            continue

        result = flag_trip(
            trip_id,
            cash_submissions[trip_id],
            fare_per_passenger,
            db_path
        )

        if result["status"] == "Verified":
            verified.append(result)
        elif result["status"] == "Not Applicable":
            not_applicable.append(result)
        else:
            needs_review.append(result)

    return {
        "taxi_id": taxi_id,
        "total_trips_checked": len(verified) + len(needs_review) + len(not_applicable) + len(no_submission),
        "verified_count": len(verified),
        "needs_review": needs_review,
        "no_submission": no_submission,
        "not_applicable_count": len(not_applicable)
    }


if __name__ == "__main__":
    print(flag_trip(trip_id=12, cash_submitted=75, fare_per_passenger=25))
    print(flag_trip(trip_id=14, cash_submitted=60, fare_per_passenger=25))
    print(flag_trip(trip_id=18, cash_submitted=30, fare_per_passenger=25))
    print(flag_trip(trip_id=19, cash_submitted=0, fare_per_passenger=25))

    cash_submissions = {
        12: 75,
        14: 60,
        18: 30
    }

    print(generate_flag_report(taxi_id="MT64TP GP", cash_submissions=cash_submissions, fare_per_passenger=25))