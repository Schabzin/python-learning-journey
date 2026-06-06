import sqlite3
import bcrypt

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS taxis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT UNIQUE NOT NULL,
            driver_name TEXT,
            driver_phone TEXT,
            route TEXT,
            current_km INTEGER DEFAULT 0,
            last_service_km INTEGER DEFAULT 0,
            next_service_km INTEGER DEFAULT 0,
            last_service_date DATE,
            status TEXT DEFAULT 'active',
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)


    routes = ["CBD", "VaalMall", "River", "Mittal"]
    for route in routes:
        cursor.execute("INSERT OR IGNORE INTO routes (name) VALUES (?)", (route,))

    conn.commit()
    conn.close()
    print("Taxi database created successfully!")

def create_default_users():
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()
    hashed = bcrypt.hashpw("kalikeng2026".encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                       ("chahane", hashed, "owner"))
        conn.commit()
        print("Default user created")
    except sqlite3.IntegrityError:
        print("User already exists")
    conn.close()

def create_default_taxis():
    conn = sqlite3.connect("taxi.db")
    cursor = conn.cursor()
    taxis = [
        ("GP123456", "Driver 1", "Chahane"),
        ("GP234567", "Driver 2", "Tshidiso"),
        ("GP345678", "Driver 3", "Oupa"),
    ]
    for plate, driver, phone in taxis:
        try:
            cursor.execute("""
                INSERT INTO taxis (plate, driver_name, driver_phone, status)
                VALUES (?, ?, ?, 'active')
            """, (plate, driver, phone))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
               
    print("Default taxis created")
    cursor.execute("UPDATE taxis SET driver_name=?, driver_phone=? WHERE plate=?",
                   ("Chahane", "0711111111", "GP123456"))
    cursor.execute("UPDATE taxis SET driver_name=?, driver_phone=? WHERE plate=?",
                   ("Tshidiso", "0722222222", "GP234567"))
    cursor.execute("UPDATE taxis SET driver_name=?, driver_phone=? WHERE plate=?",
                   ("Oupa", "0733333333", "GP345678"))
    conn.commit()
    conn.close()

init_db()
create_default_users()
create_default_taxis()