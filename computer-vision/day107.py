import sqlite3
from datetime import datetime

DB_PATH = "passenger_counts.db"

def create_passenger_tables():
    """
    Two tables: trips (one row per counting session, e.g.one taxi's morning run)
    and crossings (one row per individual IN/OUT event, tied to a trip).
    Separating them lets you query "total passengers today" without losing
    the detail of exactly when each person boarded or alighted.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxi_id TEXT NOT NULL,
            date_started TEXT NOT NULL,
            time_started TEXT NOT NULL,
            date_ended TEXT,
            time_ended TEXT,
            final_in_count INTEGER DEFAULT 0,
            final_out_count INTEGER DEFAULT 0,
            final_net_occupancy INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crossings (
            crossing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            direction TEXT NOT NULL,
            track_id INTEGER NOT NULL,
            running_net INTEGER NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
        )
    """)

    conn.commit()
    conn.close()
    print("Passenger count tables ready.")

def start_trip(taxi_id):
    """Call once when a counting session begins (e.g. taxi leaves the rank)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO trips (taxi_id, date_started, time_started)
        VALUES (?, ?, ?)
    """, (taxi_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
    trip_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trip_id

def log_crossing(trip_id, direction, track_id, running_net):
    """Call every time a real IN or OUT crossing is confirmed by the counter."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net)
        VALUES (?, ?, ?, ?, ?)
    """, (trip_id, now.strftime("%Y-%m-%d %H:%M:%S"), direction, track_id, running_net))
    conn.commit()
    conn.close()

def end_trip(trip_id, final_in, final_out, final_net):
    """Call once when the counting session ends (e.g. taxi returns to the rank)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        UPDATE trips
        SET date_ended = ?, time_ended = ?, final_in_count = ?, final_out_count = ?, final_net_occupancy = ?
        WHERE trip_id = ?
    """, (now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), final_in, final_out, final_net, trip_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_passenger_tables()

    print("\nSimulating a test trip...")
    test_trip_id = start_trip(taxi_id="TEST-VAN-01")
    print(f"Trip started, trip_id={test_trip_id}")

    log_crossing(test_trip_id, direction="IN", track_id=0, running_net=1)
    log_crossing(test_trip_id, direction="IN", track_id=1, running_net=2)
    log_crossing(test_trip_id, direction="OUT", track_id=0, running_net=1)

    end_trip(test_trip_id, final_in=2, final_out=1, final_net=1)
    print("Trip ended and saved.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trips WHERE trip_id = ?", (test_trip_id,))
    print("\nTrip record from database:", cursor.fetchone())
    cursor.execute("SELECT * FROM crossings WHERE trip_id =?", (test_trip_id,))
    print("Crossing from database:")
    for row in cursor.fetchall():
        print(" ", row)
    conn.close()