"""cleanup_test_duplicate.py -- removes the test row we added."""
import sqlite3

DB_PATH = r"C:\Users\Sechaba\Desktop\python\taxi.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM queue WHERE id = 104")
conn.commit()
conn.close()

print("Deleted test duplicate (queue id=104).")