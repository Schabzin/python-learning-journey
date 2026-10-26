import datetime
import sqlite3
from blueprints.reports import period_rows

D = datetime.date

def make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE taxis (id INTEGER PRIMARY KEY, plate TEXT, driver_name TEXT, owner_id INTEGER);
        CREATE TABLE trips (id INTEGER PRIMARY KEY, taxi_id INTEGER, timestamp DATETIME);
        CREATE TABLE daily_targets (id INTEGER PRIMARY KEY, taxi_id INTEGER, date DATE,
                                    collected_amount REAL);
        INSERT INTO taxis VALUES (1, 'MINE 001', 'Driver A', 7),
                                 (2, 'MINE 002', 'Driver B', 7),
                                 (3, 'OTHER 001', 'Driver C', 8);
    """)
    for day, cash in [("2026-10-01", 800), ("2026-10-02", 700)]:
        for _ in range(6):
            conn.execute("INSERT INTO trips (taxi_id, timestamp) VALUES (1, ?)", (day + " 08:00:00",))
        conn.execute("INSERT INTO daily_targets (taxi_id, date, collected_amount) VALUES (1, ?, ?)",
                     (day, cash))
    conn.execute("INSERT INTO trips (taxi_id, timestamp) VALUES (3, '2026-10-01 09:00:00')")
    conn.execute("INSERT INTO daily_targets (taxi_id, date, collected_amount) VALUES (3, '2026-10-01', 9999)")
    return conn


def test_no_fan_out():
    rows = period_rows(make_db().cursor(), 7, D(2026, 10, 1), D(2026, 10, 2))
    mine = rows[0]
    assert mine["plate"] == "MINE 001"
    assert mine["trips"] == 12
    assert mine["collected"] == 1500


def test_only_my_taxis():
    rows = period_rows(make_db().cursor(), 7, D(2026, 10, 1), D(2026, 10, 2))
    assert [r["plate"] for r in rows] == ["MINE 001", "MINE 002"]


def test_taxi_with_nothing_still_shows():
    rows = period_rows(make_db().cursor(), 7, D(2026, 10, 2), D(2026, 10, 2))
    assert rows[1]["trips"] == 0
    assert rows[1]["collected"] == 0


def test_both_ends_included():
    rows = period_rows(make_db().cursor(), 7, D(2026, 10, 2), D(2026, 10, 2))
    assert rows[0]["collected"] == 700

