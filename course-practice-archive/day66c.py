from contextlib import contextmanager
import sqlite3

@contextmanager
def get_taxi_db():
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

with get_taxi_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM taxis")
    taxis = [dict(row) for row in cursor.fetchall()]
    print(taxis)