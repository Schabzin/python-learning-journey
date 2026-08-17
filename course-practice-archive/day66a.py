import sqlite3

def safe_km_update(current_km_str):
    try:
        km = int(current_km_str)
        return km
    except ValueError:
        return "Invalid KM - please enter a number"

def safe_db_query(taxi_id):
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM taxis WHERE id = ?", (taxi_id,))
        taxi = cursor.fetchone()
        return dict(taxi) if taxi else None
    except sqlite3.OperationalError as e:
        return f"Database error: {e}"
    finally:
        conn.close()

print(safe_km_update("12500"))
print(safe_km_update("abc"))
print(safe_db_query(1))
print(safe_db_query(9999))



