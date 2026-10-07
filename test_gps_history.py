"""
test_gps_history.py
Proves gps_history records and reads pings correctly.
Every test uses a throwaway database, never taxi.db.
"""
import sqlite3
from datetime import datetime, timezone, timedelta

import pytest

from gps_history import (
    PingError, parse_recorded_at, parse_accuracy, save_ping, get_pings, delete_old_pings
)

FIXED_NOW = datetime(2026, 10, 7, 8, 0, 0, tzinfo=timezone.utc)
SA = timezone(timedelta(hours=2))

@pytest.fixture
def db(tmp_path):
    path = tmp_path / "test.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE taxis (id INTEGER PRIMARY KEY, plate TEXT)")
    conn.execute("INSERT INTO taxis (id, plate) VALUES (1, 'AAA111GP'), (2, 'BBB222GO')")
    conn.execute("""
        CREATE TABLE gps_pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxi_id INTEGER NOT NULL,
            lat REAL NOT NULL CHECK (lat BETWEEN -90 AND 90),
            lon REAL NOT NULL CHECK (lon BETWEEN -180 AND 180),
            recorded_at DATETIME NOT NULL,
            received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            accuracy_m REAL CHECK (accuracy_m IS NULL OR accuracy_m >= 0),
            FOREIGN KEY (taxi_id) REFERENCES taxis(id))""")
    conn.commit()
    conn.close()
    return str(path)

def test_sa_time_becomes_utc():
    assert parse_recorded_at("2026-10-07T09:22:05+02:00", now=FIXED_NOW) == "2026-10-07 07:22:05"

def test_z_means_utc():
    assert parse_recorded_at("2026-10-07T07:22:05Z", now=FIXED_NOW) == "2026-10-07 07:22:05"

def test_missing_time_uses_now():
    assert parse_recorded_at(None, now=FIXED_NOW) == "2026-10-07 08:00:00"

@pytest.mark.parametrize("bad, message", [
    ("2026-10-07T09:22:05", "time zone"),
    ("yesterday", "not a valid ISO time"),
    (12345, "must be text"),
    ("2026-10-07T08:05:00Z", "in the future"),
])
def test_bad_time_rejected(bad, message):
    with pytest.raises(PingError, match=message):
        parse_recorded_at(bad, now=FIXED_NOW)

def test_one_minute_fast_clock_allowed():
    assert parse_recorded_at("2026-10-07T08:01:00Z", now=FIXED_NOW) == "2026-10-07 08:01:00"

def test_accuracy_optional_and_numeric():
    assert parse_accuracy(None) is None
    assert parse_accuracy("12.5") == 12.5

@pytest.mark.parametrize("bad", [True, -1, "far"])
def test_bad_accuracy_rejected(bad):
    with pytest.raises(PingError):
        parse_accuracy(bad)

def test_ping_round_trip_in_time_order(db):
    save_ping(1, -26.70, 27.83, "2026-10-07 07:10:00", 8.0, db_path=db)
    save_ping(1, -26.68, 27.84, "2026-10-07 07:00:00", None, db_path=db)

    pings = get_pings(1, datetime(2026, 10, 7, 9, 0, tzinfo=SA),
                         datetime(2026, 10, 7, 9, 30, tzinfo=SA), db_path=db)

    assert [p["lat"] for p in pings] == [-26.68, -26.70]
    assert pings[0]["time"] == datetime(2026, 10, 7, 7, 0, tzinfo=timezone.utc)
    assert pings[1]["accuracy_m"] == 8.0

def test_window_and_taxi_filter(db):
    save_ping(1, -26.70, 27.83, "2026-10-07 06:59:59", db_path=db)
    save_ping(1, -26.70, 27.83, "2026-10-07 07:15:00", db_path=db)
    save_ping(2, -26.70, 27.83, "2026-10-07 07:15:00", db_path=db)
    save_ping(1, -26.70, 27.83, "2026-10-07 07:30:01", db_path=db)

    pings = get_pings(1, datetime(2026, 10, 7, 7, 0, tzinfo=timezone.utc),
                         datetime(2026, 10, 7, 7, 30, tzinfo=timezone.utc), db_path=db)
    assert len(pings) == 1

def test_unknown_taxi_refused_by_database(db):
    with pytest.raises(sqlite3.IntegrityError):
        save_ping(99, -26.70, 27.83, "2026-10-07 07:00:00", db_path=db)

def test_get_pings_rejects_bad_windows(db):
    start = datetime(2026, 10, 7, 7, 30, tzinfo=timezone.utc)
    end = datetime(2026, 10, 7, 7, 0, tzinfo=timezone.utc)
    with pytest.raises(PingError, match="before start"):
        get_pings(1, start, end, db_path=db)
    with pytest.raises(PingError, match="time zone"):
        get_pings(1, datetime(2026, 10, 7, 7, 0), end, db_path=db)

def test_old_pings_deleted_recent_kept(db):
    save_ping(1, -26.70, 27.83, "2026-07-01 07:00:00", db_path=db)
    save_ping(1, -26.70, 27.83, "2026-09-01 07:00:00", db_path=db)

    deleted = delete_old_pings(90, now=FIXED_NOW, db_path=db)

    assert deleted == 1
    left = get_pings(1, datetime(2026, 1, 1, tzinfo=timezone.utc), FIXED_NOW, db_path=db)
    assert len(left) == 1

@pytest.mark.parametrize("bad", [0, -5, 1.5, True, "90"])
def test_bad_retention_rejected(db, bad):
    with pytest.raises(PingError):
        delete_old_pings(bad, now=FIXED_NOW, db_path=db)