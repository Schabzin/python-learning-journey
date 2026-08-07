import sqlite3
import bcrypt
import os

def get_db_path():
    if os.path.exists("/data"):
        return "/data/taxi.db"
    return "taxi.db"

def init_db():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'marshall',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_until DATE DEFAULT NULL
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
            driver_username TEXT,
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)


    routes = ["CBD", "VaalMall", "River", "Mittal"]
    for route in routes:
        cursor.execute("INSERT OR IGNORE INTO routes (name) VALUES (?)", (route,))

    conn.commit()
    conn.close()
    print("Taxi database created successfully!")

def create_default_users():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    hashed = bcrypt.hashpw("kalikeng2026".encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                       ("chahane", hashed, "owner"))
        conn.commit()
        print("Default user created")
    except sqlite3.IntegrityError:
        print("User already exists")
    hashed_driver = bcrypt.hashpw("separaka123".encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                       ("oupa_driver", hashed_driver, "driver"))
        conn.commit()
        print("Driver user created")
    except sqlite3.IntegrityError:
        print("Driver user already exists")

    hashed_marshall = bcrypt.hashpw("marshall123".encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("marshall1", hashed_marshall, "marshall"))
        conn.commit()
        print("Marshall user created")
    except sqlite3.IntegrityError:
        print("Marshall user already exists")

    hashed_admin = bcrypt.hashpw("separaka_admin_2026".encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("sechaba_admin", hashed_admin, "owner"))
        conn.commit()
        print("Admin user created")
    except sqlite3.IntegrityError:
        print("Admin user already exists")
    conn.close()

def create_default_taxis():
    print("Skipping default taxis - owners add their own taxis now")
  

def add_created_at_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
        conn.commit()
        print("created_at column added")
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_paid_until_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN paid_until DATE DEFAULT NULL")
        conn.commit()
        print("paid_until column added")
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_platform_support():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rank_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taxi_id INTEGER NOT NULL,
            platform_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            status TEXT DEFAULT 'waiting',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for table in ["taxis", "routes", "users"]:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col["name"] for col in cursor.fetchall()]
        if "platform_id" not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN platform_id INTEGER")

    conn.commit()
    conn.close()

def add_email_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
        print("email column added")
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_layer_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE queue ADD COLUMN layer TEXT")
        conn.commit()
        print("layer column added")
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_layers_table():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS layers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (platform_id) REFERENCES platforms(id),
            UNIQUE(platform_id, name)
        )
    """)
    conn.commit()
    conn.close()

def seed_layers():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM platforms WHERE name = 'Platform 1'")
    platform_1 = cursor.fetchone()
    if platform_1:
        layers = ["Straight Evaton", "Eastern road", "Zone 3 via Residensia", "Zone 8 Smallfarm"]
        for layer_name in layers:
            cursor.execute("INSERT OR IGNORE INTO layers (platform_id, name) VALUES (?, ?)",
                           (platform_1["id"], layer_name))
    conn.commit()
    conn.close()



init_db()
create_default_users()
create_default_taxis()
add_created_at_column()
add_paid_until_column()
add_platform_support()
add_email_column()
add_layer_column()
add_layers_table()
seed_layers()