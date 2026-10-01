import sqlite3

conn = sqlite3.connect(r"C:\Users\Sechaba\Desktop\python\taxi.db")
conn.execute("UPDATE routes SET fare_per_passenger = 25 WHERE id = 20")
conn.commit()
conn.close()
print("done")