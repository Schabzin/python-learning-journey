"""add_test_duplicate.py -- deliberately creates a duplicate queue entry
to prove find_queue_integrity_issues() catches it. Delete this test row
afterward using its printed id."""
import sqlite3

DB_PATH = r"C:\Users\Sechaba\Desktop\python\taxi.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO queue (taxi_id, platform_id, layer, position, status)
    VALUES (7, 3, 'Zone 28/GG', 2, 'waiting')
""")
conn.commit()

new_id = cursor.lastrowid
print(f"Inserted test duplicate: queue id={new_id}. Remember this number -- you'll delete it after.")

conn.close()