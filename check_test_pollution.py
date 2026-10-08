"""
check_test_pollution.py
Read-only: counts rows the old test_corroboration.py script
left behind in whatevere database get_db_path() points at.
"""
import sqlite3

from utils import get_db_path

FINGERPRINT = ("12:30:00", "12:30:45")

path = get_db_path()
print("Database:", path)

conn = sqlite3.connect(path)
try:
    crossings = conn.execute(
        "SELECT COUNT(*) FROM crossings WHERE timestamp IN (?, ?)",
        FINGERPRINT,
    ).fetchone()[0]
    trips = conn.execute(
        """SELECT COUNT(*) FROM trips
           WHERE id IN (SELECT trip_id FROM crossings
                        WHERE timestamp IN (?, ?))""",
        FINGERPRINT,
    ).fetchone()[0]
finally:
    conn.close()

print("Fake crossings found:", crossings)
print("Fake trips found:", trips)