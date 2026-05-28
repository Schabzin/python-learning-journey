import sqlite3

def init_db():
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'marshall'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxi_id INTEGER,
            route_id INTEGER,
            logged_by INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (taxi_id) REFERENCES taxis(id),
            FOREIGN KEY (route_id) REFERENCES route(id),
            FOREIGN KEY (logged_by) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxi_id INTEGER,
            date DATE DEFAULT CURRENT_DATE,
            target_amount REAL DEFAULT 750.00,
            collected_amount REAL DEFAULT 0.00,
            FOREIGN KEY (taxi_id) REFERENCES taxis(id)
        )
    """)

    routes = ["CBD", "VaalMall", "River", "Mittal"]
    for route in routes:
        cursor.execute("INSERT OR IGNORE INTO routes (name) VALUES (?)", (route,))

    conn.commit()
    conn.close()
    print("Taxi database created successfully!")

init_db()