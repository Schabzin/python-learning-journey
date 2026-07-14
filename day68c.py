import itertools
from contextlib import contextmanager
import sqlite3
from datetime import date

@contextmanager
def get_taxi_db():
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def fetch_trips_by_owner(owner_id):
    """Yields trip records one at a time for a specific owner"""
    with get_taxi_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tr.id, tr.taxi_id, tr.timestamp, t.plate, t.driver_name
            FROM trips tr
            JOIN taxis t ON tr.taxi_id = t.id
            WHERE t.owner_id = ?
            ORDER BY tr.timestamp DESC
        """, (owner_id,))
        while True:
            row = cursor.fetchone()
            if row is None:
                return
            yield dict(row)

def first_n(generator, n):
    return list(itertools.islice(generator, n))

def build_daily_report(owner_id, date):
    """Builds a daily report line by line"""
    yield f"=== Daily Report: {date} ==="
    yield f"Owner ID: {owner_id}"
    yield ""

    total_trips = 0
    for trip in fetch_trips_by_owner(owner_id):
        if trip["timestamp"].startswith(date):
            total_trips += 1
            yield f"  {trip['plate']} logged a trip at {trip['timestamp']}"

    yield ""
    yield f"Total trips: {total_trips}"

today = date.today().isoformat()

for line in build_daily_report(1, today):
    print(line)

trips = fetch_trips_by_owner(1)
print(first_n(trips, 3))




