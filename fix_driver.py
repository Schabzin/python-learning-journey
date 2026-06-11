import sqlite3
conn = sqlite3.connect("taxi.db")
conn.execute("UPDATE taxis SET driver_name='oupa_driver' WHERE plate='GP345678'")
conn.commit()
conn.close()
print("Done")