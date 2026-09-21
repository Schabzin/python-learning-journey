import os
import sqlite3
import pytest
from geofencing import detect_zone_transition
from geofencing import is_within_geofence

TEST_DB_PATH = "test_geofencing.db"

@pytest.fixture
def test_db():
    """
    Builds a small, throwaway database with exactly the two tables
    detect_zone_transition() needs -- taxis (for last_known_zone_id) and
    geofence_zones (for the actual zone to detect entry into). Deleted
    after the test runs so it never pollutes your real taxi.db or leaves
    junk files behind between test runs.
    """
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE taxis (
            id INTEGER PRIMARY KEY,
            plate TEXT,
            last_known_zone_id INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE geofence_zones (
            id INTEGER PRIMARY KEY,
            name TEXT,
            zone_type TEXT,
            center_lat REAL,
            center_lon REAL,
            radius_meters REAL
        )
    """)

    cursor.execute(
        "INSERT INTO taxis (id, plate, last_known_zone_id) VALUES (1, 'MT64TP GP', NULL)"
    )
    cursor.execute("""
        INSERT INTO geofence_zones (id, name, zone_type, center_lat, center_lon, radius_meters)
        VALUES (1, 'Test Rank Zone', 'rank', -26.7096, 27.8367, 40.0)
    """)

    conn.commit()
    conn.close()

    yield TEST_DB_PATH

    os.remove(TEST_DB_PATH)

def test_detect_zone_transition_entered_zone(test_db):
    result = detect_zone_transition(
        taxi_id=1,
        current_lat=-26.7096,
        current_lon=27.8367,
        db_path=test_db
    )

    assert result["event"] == "entered_zone"
    assert result["zone_id"] == 1

def test_is_within_geofence_point_inside():
    assert is_within_geofence(
        taxi_lat=-26.7096, taxi_lon=27.8367,
        zone_lat=-26.7096, zone_lon=27.8367,
        radius_meters=40.0
    ) is True

def test_is_within_geofence_point_outside():
    assert is_within_geofence(
        taxi_lat=-26.8000, taxi_lon=27.9000,
        zone_lat=-26.7096, zone_lon=27.8367,
        radius_meters=40.0
    ) is False



