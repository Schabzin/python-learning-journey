"""
test_ping_uniqueness.py
One reading (same taxi + same recorded_at) must be stored once -- whether it
arrives twice from a phone, or already sits twice in an old database.
"""
import sqlite3
import pytest
from gps_history import save_ping
from setup_taxi_db import make_gps_pings_unique

READING_TIME = "2026-10-11 14:43:46"

def taxi_id(db_path, plate):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(
            "SELECT id FROM taxis WHERE plate = ?", (plate,)
        ).fetchone()[0]
    finally:
        conn.close()

def count_pings(db_path):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM gps_pings").fetchone()[0]
    finally:
        conn.close()

def test_same_reading_twice_is_stored_once(test_db):
    taxi = taxi_id(test_db, "TEST01GP")

    first = save_ping(taxi, -26.58, 27.84, READING_TIME, 20.0, db_path=test_db)
    second = save_ping(taxi, -26.58, 27.84, READING_TIME, 20.0, db_path=test_db)

    assert isinstance(first, int)
    assert second is None
    assert count_pings(test_db) == 1

def test_same_time_on_two_taxis_is_two_readings(test_db):
    mine = taxi_id(test_db, "TEST01GP")
    other = taxi_id(test_db, "OTHER2GP")

    assert save_ping(mine, -26.58, 27.84, READING_TIME, db_path=test_db) is not None
    assert save_ping(other, -26.60, 27.85, READING_TIME, db_path=test_db) is not None
    assert count_pings(test_db) == 2

def test_broken_data_still_raises(test_db):
    taxi = taxi_id(test_db, "TEST01GP")

    with pytest.raises(sqlite3.IntegrityError):
        save_ping(taxi, 200.0, 27.84, READING_TIME, db_path=test_db)

    assert count_pings(test_db) == 0

def test_cleanup_fixes_an_old_database(test_db):
    taxi = taxi_id(test_db, "TEST01GP")

    conn = sqlite3.connect(test_db)
    with conn:
        conn.execute("DROP INDEX idx_gps_pings_unique_reading")
        for _ in range(3):
            conn.execute(
                "INSERT INTO gps_pings (taxi_id, lat, lon, recorded_at) VALUES (?, ?, ?, ?)",
                (taxi, -26.58, 27.84, READING_TIME),
            )
        conn.execute(
            "INSERT INTO gps_pings (taxi_id, lat, lon, recorded_at) VALUES (?, ?, ?, ?)",
            (taxi, -26.59, 27.85, "2026-10-11 15:36:10"),
        )
    first_id = conn.execute("SELECT MIN(id) FROM gps_pings").fetchone()[0]
    conn.close()

    make_gps_pings_unique() 
    make_gps_pings_unique()

    conn = sqlite3.connect(test_db)
    try:
        kept = conn.execute(
            "SELECT id, recorded_at FROM gps_pings ORDER BY id"
        ).fetchall()
        indexes = {row[1]: row[2] for row in conn.execute("PRAGMA index_list(gps_pings)")}
    finally:
        conn.close()

    assert kept == [(first_id, READING_TIME), (first_id + 3, "2026-10-11 15:36:10")]
    assert indexes.get("idx_gps_pings_unique_reading") == 1