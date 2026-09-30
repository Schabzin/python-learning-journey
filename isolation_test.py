import sqlite3
from utils import get_db_path

conn = sqlite3.connect(get_db_path(), timeout=1)
try:
    conn.execute(
        "INSERT INTO geofence_zones (name, center_lat, center_lon, radius_meters, active) "
        "VALUES ('isolatation_test', 0, 0, 10, 1)"
    )
    conn.commit()
    print("SUCCESS")
except Exception as e:
    print("FAILED:", e)
finally:
    conn.close()