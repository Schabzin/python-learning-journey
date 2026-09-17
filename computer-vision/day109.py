import sqlite3

DB_PATH = "passenger_counts.db"

def get_connection(db_path=DB_PATH):
    """
    Opens a connection to the trips database with foreign keys enforced.
    PRAGMA foreign_keys=ON must be set on every connection --
    SQLite does not enforce foreign keys by default, even if
    the schema defines them.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def upgrade_schema_add_route_type(db_path=DB_PATH):
    """
    Adds a route-type column to the existing trips table.
    'revenue' = normal paid leg, fare expected.
    'feeder' = free leg, no fare expected from this taxi for this leg.
    Default is 'revenue' so existing trips aren't silently reclassified.
    """

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(trips)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "route_type" not in existing_columns:
        cursor.execute("""
            ALTER TABLE trips
            ADD COLUMN route_type TEXT NOT NULL DEFAULT 'revenue'
        """)
        conn.commit()
        print("route_type column added successfully.")
    else:
        print("route_type column already exists -- no changes made.")

    conn.close()

def start_trip(taxi_id, route_type="revenue", db_path=DB_PATH):
    """
    Starts a new trip, now requiring an explicit route_type decision
    up front rather than defaulting silently mid-trip.
    route_type must be either 'revenue' or 'feeder'.
    """
    if route_type not in ("revenue", "feeder"):
        raise ValueError(f"Invalid route_type: {route_type}")

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trips (taxi_id, date_started, time_started, route_type)
        VALUES (?, DATE('now'), TIME('now'), ?)
    """, (taxi_id, route_type))

    trip_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"Trip {trip_id} started for taxi {taxi_id} as a '{route_type}' leg.")
    return trip_id

def calculate_expected_revenue(trip_id, fare_per_passenger, db_path=DB_PATH):
    """
    Calculates expected revenue for a trip -- but only if it's
    a revenue-type leg. Feeder legs return 0 by design, since no
    fare was ever meant to be collected on that specific taxi.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT route_type FROM trips WHERE trip_id = ?
    """, (trip_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        raise ValueError(f"No trip found with id {trip_id}")

    route_type = result[0]

    if route_type == "feeder":
        conn.close()
        print(f"Trip {trip_id} (feeder): R0 -- free leg, no fare expected on this taxi.")
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

if __name__ == "__main__":
    upgrade_schema_add_route_type()
    revenue_trip_id = start_trip(taxi_id="MT64TP GP", route_type="revenue")
    feeder_trip_id = start_trip(taxi_id="MT64TP GP", route_type="feeder")
    conn = get_connection()
    cursor = conn.cursor()
    for i in range(3):
        cursor.execute("""
            INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net)
            VALUES (?, TIME('now'), 'IN', ?, ?)
        """, (revenue_trip_id, i, i + 1))
    conn.commit()
    conn.close()

    calculate_expected_revenue(feeder_trip_id, fare_per_passenger=25)
    calculate_expected_revenue(revenue_trip_id, fare_per_passenger=25)