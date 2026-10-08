"""
test_corroboration.py
Cross-taxi corroboration, tested on a throwaway database.
Replaces an old script that wrote fake trips into the real taxi.db.
"""
import sqlite3
import pytest
from corroboration import find_corroborating_cross_taxi_event

def make_trip(conn, plate, route_type):
    """Start a trip for the taxi with this plate. Returns (taxi_id, trip_id)."""
    taxi_id = conn.execute(
        "SELECT id FROM taxis WHERE plate = ?", (plate,)).fetchone()[0]
    cursor = conn.execute(
        "INSERT INTO trips (taxi_id, route_id, route_type, logged_by, timestamp) "
        "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (taxi_id, 13, route_type, 1),
    )
    return taxi_id, cursor.lastrowid

def add_crossing(conn, trip_id, timestamp, direction, running_net):
    conn.execute(
        "INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net) "
        "VALUES (?, ?, ?, ?, ?)",
        (trip_id, timestamp, direction, 1, running_net),
    )

@pytest.fixture
def handover(test_db):
    """Taxi A lets a passenger OUT at 12:30:00; taxi B takes one IN at 12:30:45."""
    conn = sqlite3.connect(test_db)
    with conn:
        _, trip_a = make_trip(conn, "TEST01GP", "feeder")
        taxi_b, trip_b = make_trip(conn, "OTHER2GP", "revenue")
        add_crossing(conn, trip_a, "12:30:00", "OUT", 0)
        add_crossing(conn, trip_b, "12:30:45", "IN", 1)
    conn.close()
    return {"db": test_db, "trip_a": trip_a, "trip_b": trip_b, "taxi_b": taxi_b}

def test_matching_event_on_other_taxi_corroborates(handover):
    result = find_corroborating_cross_taxi_event(
        trip_id=handover["trip_a"],
        direction="OUT",
        event_timestamps=["12:30:00"],
        db_path=handover["db"],
    )

    assert result["status"] == "Corroborated"
    assert len(result["matching_taxi_events"]) == 1
    match = result["matching_taxi_events"][0]
    assert match["taxi_id"] == handover["taxi_b"]
    assert match["trip_id"] == handover["trip_b"]

def test_far_off_time_stands_alone(handover):
    result = find_corroborating_cross_taxi_event(
        trip_id=handover["trip_a"],
        direction="OUT",
        event_timestamps=["18:00:00"],
        db_path=handover["db"],
    )

    assert result["status"] == "No Corroboration Found"
    assert result["matching_taxi_events"] == []
    