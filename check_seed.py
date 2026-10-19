import sqlite3

conn = sqlite3.connect("taxi.db")

trips = conn.execute(
    "SELECT COUNT(*) FROM trips tr JOIN taxis t ON t.id = tr.taxi_id "
    "WHERE t.plate LIKE 'DEMO %'"
).fetchone()[0]
targets = conn.execute(
    "SELECT COUNT(*) FROM daily_targets dt JOIN taxis t ON t.id = dt.taxi_id "
    "WHERE t.plate LIKE 'DEMO %'"
).fetchone()[0]
print(f"trips: {trips} (expected 122)  daily_targets: {targets} (expected 21)")

rows = conn.execute("""
    SELECT t.plate, dt.date, dt.collected_amount, dt.target_amount,
           (SELECT COUNT(*) FROM trips tr
             WHERE tr.taxi_id = dt.taxi_id AND DATE(tr.timestamp) = dt.date) AS trip_count
    FROM daily_targets dt JOIN taxis t ON t.id = dt.taxi_id
    WHERE t.plate LIKE 'DEMO %' AND dt.collected_amount < dt.target_amount
""").fetchall()
for plate, day, got, target, n in rows:
    print(f"SHORT: {plate} on {day}: R{got:.0f} of R{target:.0f}, {n} trips")

conn.close()