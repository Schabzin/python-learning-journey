import sqlite3
import pytest
from geofencing import detect_zone_transition

ZONE_A = (-26.7089, 27.8146)
ZONE_B = (-26.7150, 27.8200)
OUTSIDE = (-26.9000, 27.9000)

@pytest.fixture
def test_db(tmp_path):
    """
    Builds a fresh, throwaway SQLite database for each test -- tmp_path is
    a pytest-provided temporary folder that gets deleted automatically
    after the test runs, so nothing here ever touches passenger_counts.db.
    """
    db_path = tmp_path / "test_taxis.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE taxis (
            id INTEGER PRIMARY KEY,
            plate TEXT,
            last_known_zone_id INTEGER,
            pending_zone_id INTEGER,
            pending_zone_count INTEGER DEFAULT 0,
            last_ping_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE geofence_zones (
            id INTEGER PRIMARY KEY,
            center_lat REAL,
            center_lon REAL,
            radius_meters REAL
        )
    """)

    cursor.execute("INSERT INTO taxis (id, plate) VALUES (1, 'TEST-001')")
    cursor.execute(
        "INSERT INTO geofence_zones (id, center_lat, center_lon, radius_meters) VALUES (1, ?, ?, 100)",
        ZONE_A
    )
    cursor.execute(
        "INSERT INTO geofence_zones (id, center_lat, center_lon, radius_meters) VALUES (2, ?, ?, 100)",
        ZONE_B
    )
    conn.commit()
    conn.close()

    return str(db_path)

def test_pure_entry(test_db):
    result = detect_zone_transition(1, *ZONE_A, db_path=test_db)
    assert result["event"] == "no_change"

    result = detect_zone_transition(1, *ZONE_A, db_path=test_db)
    assert result["event"] == "entered_zone"
    assert result["zone_id"] == 1
    assert result["previous_zone_id"] is None

def test_pure_exit(test_db):
    detect_zone_transition(1, *ZONE_A, db_path=test_db)
    detect_zone_transition(1, *ZONE_A, db_path=test_db)

    detect_zone_transition(1, *OUTSIDE, db_path=test_db)
    result = detect_zone_transition(1, *OUTSIDE, db_path=test_db)

    assert result["event"] == "exited_zone"
    assert result["zone_id"] is None
    assert result["previous_zone_id"] == 1

def test_direct_handoff(test_db):
    detect_zone_transition(1, *ZONE_A, db_path=test_db)
    detect_zone_transition(1, *ZONE_A, db_path=test_db)

    detect_zone_transition(1, *ZONE_B, db_path=test_db)
    result = detect_zone_transition(1, *ZONE_B, db_path=test_db)

    assert result["event"] == "changed_zone"
    assert result["zone_id"] == 2
    assert result["previous_zone_id"] == 1

