import sqlite3
from datetime import datetime
from corroboration import find_corroborating_cross_taxi_event

DB_PATH = r"C:\Users\Sechaba\Desktop\python\taxi.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute(
    "INSERT INTO trips (taxi_id, route_id, route_type, logged_by, timestamp) "
    "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
    (1, 13, "feeder", 1)
)
trip_1_id = cursor.lastrowid

cursor.execute(
    "INSERT INTO trips (taxi_id, route_id, route_type, logged_by, timestamp) "
    "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
    (2, 13, "revenue", 1)
)
trip_2_id = cursor.lastrowid

cursor.execute(
    "INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net) "
    "VALUES (?, ?, 'OUT', ?, ?)",
    (trip_1_id, "12:30:00", 1, 0)
)
cursor.execute(
    "INSERT INTO crossings (trip_id, timestamp, direction, track_id, running_net) "
    "VALUES (?, ?, 'IN', ?, ?)",
    (trip_2_id, "12:30:45", 1, 1)
)

conn.commit()
conn.close()

print("Corroborated case:")
print(find_corroborating_cross_taxi_event(
    trip_id=trip_1_id,
    direction="OUT",
    event_timestamps=["12:30:00"],
    db_path=DB_PATH
))

print("\nUncorroborated case (far-off time, nothing should match):")
print(find_corroborating_cross_taxi_event(
    trip_id=trip_1_id,
    direction="OUT",
    event_timestamps=["18:00:00"],
    db_path=DB_PATH
))
