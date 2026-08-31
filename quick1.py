import sqlite3
conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='push_subscriptions'")
print(cursor.fetchall())
conn.close()