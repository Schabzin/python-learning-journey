"""
clean_test_pollution.py
Removes the fake trips + crossings that the old test_corroboration.py
script left in the LOCAL database.

Dry run (changes nothing):        python clean_test_pollution.py
Really delete (after a backup):   python clean_test_pollution.py --apply
"""
import os
import sqlite3
import sys
from datetime import datetime

from utils import get_db_path

FINGERPRINT = ("12:30:00", "12:30:45")
EXPECTED_CROSSINGS = 14
EXPECTED_TRIPS = 14

FAKE_TRIP_IDS_SQL = """SELECT DISTINCT trip_id FROM crossings
                       WHERE timestamp IN (?, ?)"""

def backup_database(path):
    """Copy the whole database into backups/ with a timestamp in the name."""
    folder = os.path.join(os.path.dirname(path), "backups")
    os.makedirs(folder, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(folder, f"taxi_before_cleanup_{stamp}.db")

    source = sqlite3.connect(path)
    target = sqlite3.connect(backup_path)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()
    return backup_path

def other_references(conn, trip_ids):
    """Find any table (besides crossings) that still points at these trips."""
    found = {}
    tables = [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")]
    for table in tables:
        if table == "crossings":
            continue
        columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
        if "trip_id" not in columns:
            continue
        marks = ", ".join("?" for _ in trip_ids)
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE trip_id IN ({marks})",
            trip_ids).fetchone()[0]
        if count:
            found[table] = count
    return found

def main():
    apply = "--apply" in sys.argv
    path = get_db_path()
    print("Database:", path)

    if path.startswith("/data"):
        sys.exit("STOP: this is the live Railway database. Local only.")

    conn = sqlite3.connect(path)
    try:
        trip_ids = [row[0] for row in conn.execute(FAKE_TRIP_IDS_SQL, FINGERPRINT)]
        crossings = conn.execute(
            "SELECT COUNT(*) FROM crossings WHERE timestamp IN (?, ?)",
            FINGERPRINT).fetchone()[0]
        print("Fake crossings:", crossings, "| Fake trips:", len(trip_ids))

        if crossings != EXPECTED_CROSSINGS or len(trip_ids) != EXPECTED_TRIPS:
            sys.exit("STOP: counts changed since we checked. Investigate first.")

        refs = other_references(conn, trip_ids)
        if refs:
            sys.exit(f"STOP: other tables still use these trips: {refs}")

        if not apply:
            print("Dry run only. Nothing deleted. Add --apply to delete.")
            return

        print("Backup saved to:", backup_database(path))

        marks = ", ".join("?" for _ in trip_ids)
        with conn:
            conn.execute(
                "DELETE FROM crossings WHERE timestamp IN (?,?)", FINGERPRINT)
            conn.execute(f"DELETE FROM trips WHERE id IN ({marks})", trip_ids)
        print("Deleted. Run check_test_pollution.py to confirm 0 and 0.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

        