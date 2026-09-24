"""test_queue_integrity.py -- proves find_queue_integrity_issues() catches
what it claims to catch, without ever touching the real taxi.db."""
import sqlite3
from datetime import datetime, timedelta

import pytest

from queue_integrity import find_queue_integrity_issues

NOW = datetime(2026, 9, 23, 16, 0, 0)


@pytest.fixture
def db_path(tmp_path):
    """A fresh, empty test database with just the columns this function needs."""
    path = str(tmp_path / "test.db")
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE taxis (id INTEGER PRIMARY KEY, status TEXT)")
    conn.execute("""
        CREATE TABLE queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxi_id INTEGER,
            platform_id INTEGER,
            layer TEXT,
            position INTEGER,
            status TEXT,
            joined_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    return path


def insert_taxi(db_path, taxi_id, status="active"):
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO taxis (id, status) VALUES (?, ?)", (taxi_id, status))
    conn.commit()
    conn.close()


def insert_queue_row(db_path, taxi_id, platform_id=1, status="waiting", joined_at=None):
    joined_at = joined_at or NOW.strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO queue (taxi_id, platform_id, layer, position, status, joined_at) "
        "VALUES (?, ?, 'A', 1, ?, ?)",
        (taxi_id, platform_id, status, joined_at),
    )
    conn.commit()
    conn.close()


def test_clean_queue_has_no_issues(db_path):
    insert_taxi(db_path, 1, status="active")
    insert_queue_row(db_path, taxi_id=1)  

    assert find_queue_integrity_issues(db_path, now=NOW) == []


def test_duplicate_taxi_is_flagged(db_path):
    insert_taxi(db_path, 1, status="active")
    insert_queue_row(db_path, taxi_id=1)
    insert_queue_row(db_path, taxi_id=1)  

    issues = find_queue_integrity_issues(db_path)

    duplicate_issues = [i for i in issues if i["type"] == "DUPLICATE_QUEUE_ENTRY"]
    assert len(duplicate_issues) == 1
    assert duplicate_issues[0]["taxi_id"] == 1


def test_orphaned_queue_entry_is_flagged(db_path):

    insert_queue_row(db_path, taxi_id=99)

    issues = find_queue_integrity_issues(db_path)

    orphaned = [i for i in issues if i["type"] == "ORPHANED_QUEUE_ENTRY"]
    assert len(orphaned) == 1
    assert orphaned[0]["taxi_id"] == 99


def test_inactive_taxi_in_queue_is_flagged(db_path):
    insert_taxi(db_path, 1, status="maintenance")  
    insert_queue_row(db_path, taxi_id=1)

    issues = find_queue_integrity_issues(db_path)

    inactive = [i for i in issues if i["type"] == "INACTIVE_TAXI_IN_QUEUE"]
    assert len(inactive) == 1
    assert inactive[0]["taxi_id"] == 1


def test_stale_queue_entry_is_flagged(db_path):
    insert_taxi(db_path, 1, status="active")
    old_time = (NOW - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S")
    insert_queue_row(db_path, taxi_id=1, joined_at=old_time)

    issues = find_queue_integrity_issues(db_path, stale_hours=4, now=NOW)

    stale = [i for i in issues if i["type"] == "STALE_QUEUE_ENTRY"]
    assert len(stale) == 1
    assert stale[0]["taxi_id"] == 1