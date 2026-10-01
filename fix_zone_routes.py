import sqlite3

conn = sqlite3.connect(r"C:\Users\Sechaba\Desktop\python\taxi.db")
conn.execute("UPDATE geofence_zones SET route_id = ? WHERE id = Sebokeng Rank", (route_id_for_Sebokeng Rank,))
conn.execute("UPDATE geofence_zones SET route_id = ? WHERE id = Evaton Stop", (route_id_for_Evaton Stop,))
conn.commit()
conn.close()
print("done")