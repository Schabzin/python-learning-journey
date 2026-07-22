import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM platforms")
platform = cursor.fetchone()
print("Platform found:", platform)

cursor.execute(
    "UPDATE users SET platform_id = ? WHERE username = 'marshall1'",
    (platform[0],)
)
conn.commit()
conn.close()
print("marshall1 updated")

