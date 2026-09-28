import sqlite3
from utils import get_db_path

conn = sqlite3.connect(get_db_path())
cursor = conn.cursor()

print("--- Taxis ---")
cursor.execute("SELECT id, plate FROM taxis LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("--- Geofence zones ---")
cursor.execute("SELECT id, center_lat, center_lon, radius_meters FROM geofence_zones")
for row in cursor.fetchall():
    print(row)

conn.close()