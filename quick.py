import sqlite3

conn = sqlite3.connect("taxi.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE layers")
cursor.execute("DELETE FROM queue")
conn.commit()
conn.close()
print("Layers table dropped, will be recreated cleanly on next run")