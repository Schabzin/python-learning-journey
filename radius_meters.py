import sqlite3

conn = sqlite3.connect("passenger_counts.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name, radius_meters FROM geofence_zones")

for zone_id, name, radius in cursor.fetchall():
    status = "OK" if isinstance(radius, (int, float)) and radius > 0 else "MISSING/INVALID"
    print(f"zone {zone_id} ({name}): radius_meters = {radius} [{status}]")

conn.close()