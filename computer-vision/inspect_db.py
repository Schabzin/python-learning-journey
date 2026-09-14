import sqlite3

conn = sqlite3.connect("passenger_counts.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

cursor.execute("PRAGMA table_info(trips)")
print("\ntrips columns:", cursor.fetchall())

cursor.execute("PRAGMA table_info(crossings)")
print("crossings columns:", cursor.fetchall())

cursor.execute("SELECT * FROM trips")
print("\nAll trips:")
for row in cursor.fetchall():
    print(" ", row)

cursor.execute("SELECT * FROM crossings")
print("\nAll crossings:")
for row in cursor.fetchall():
    print(" ", row)

conn.close()