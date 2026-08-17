import sqlite3

class SeparakaError(Exception):
    pass

class InvalidKMError(SeparakaError):
    pass

class TaxiNotFoundError(SeparakaError):
    pass

def update_taxi_km(taxi_id, new_km):
    if not isinstance(new_km, int):
        raise InvalidKMError(f"KM must be a number, got: {type(new_km).__name__}")
    if new_km < 0:
        raise InvalidKMError(f"KM cannot be negative: {new_km}")
    
    conn = sqlite3.connect("taxi.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM taxis WHERE id = ?", (taxi_id,))
        taxi = cursor.fetchone()
        if not taxi:
            raise TaxiNotFoundError(f"No taxi found with id {taxi_id}")
        cursor.execute("UPDATE taxis SET current_km = ? WHERE id = ?", (new_km, taxi_id))
        conn.commit()
        return f"KM updated to {new_km}"
    except TaxiNotFoundError:
        raise
    except sqlite3.OperationalError as e:
        return f"Database error: {e}"
    finally:
        conn.close()

try:
    print(update_taxi_km(1, 127000))
except (InvalidKMError, TaxiNotFoundError) as e:
    print(f"Error: {e}")

try:
    print(update_taxi_km(1, -500))
except (InvalidKMError, TaxiNotFoundError) as e:
    print(f"Error: {e}")

try:
    print(update_taxi_km(1, "abc"))
except (InvalidKMError, TaxiNotFoundError) as e:
    print(f"Error: {e}")

try:
    print(update_taxi_km(9999, 127000))
except (InvalidKMError, TaxiNotFoundError) as e:
    print(f"Error: {e}")