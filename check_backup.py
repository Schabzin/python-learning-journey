import sqlite3

path = "file:taxi.db.before_restore_day130?mode=ro"
conn = sqlite3.connect(path, uri=True)

tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for (name,) in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(name, count)

phones = conn.execute("SELECT COUNT(*) FROM taxis WHERE driver_phone IS NOT NULL").fetchone()[0]
print("taxi with a driver phone:", phones)
for table in ("users", "password_resets"):
    columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]
    print(table, columns)

for plate, phone in conn.execute("SELECT plate, driver_phone FROM taxis WHERE driver_phone IS NOT NULL"):
    print(plate, phone)

for username, email, phone in conn.execute(
        "SELECT username, email, phone FROM users WHERE email IS NOT NULL OR phone IS NOT NULL"):
    print(username, email, phone)

conn.close()