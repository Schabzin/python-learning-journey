import sqlite3
import bcrypt
import os
import re
from utils import get_db_path
from datetime import datetime

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
            ab_letter TEXT DEFAULT 'A' CHECK (ab_letter IN ('A', 'B')),
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)
    try:
        cursor.execute("ALTER TABLE taxis ADD COLUMN ab_letter TEXT DEFAULT 'A'")
        conn.commit()
        print("Migration: added ab_letter column to taxis table.")
    except sqlite3.OperationalError as error:
        if "duplicate column name" not in str(error):
            raise

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geofence_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,              -- e.g. "Platform 1 Evaton" or "Zone 3 Spar"
            zone_type TEXT NOT NULL CHECK (zone_type IN ('rank', 'destination')),
            center_lat REAL NOT NULL,
            center_lon REAL NOT NULL,
            radius_meters REAL NOT NULL DEFAULT 50.0,    -- 50m default: tight enough to
                                                            -- mean "actually at this place,"
                                                            -- loose enough for GPS drift
            route_id INTEGER,
            FOREIGN KEY (route_id) REFERENCES routes(id)
        )
    """)

    cursor.execute("""
        INSERT INTO geofence_zones (name, zone_type, center_lat, center_lon, radius_meters)
        VALUES (?, ?, ?, ?, ?)
    """, ("Platform 1 Evaton", "rank", -26.7096, 27.8367, 40.0))


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

def add_geofencing_columns():
    """
    Adds the columns detect_zone_transition() needs to the taxis table, if
    they don't already exist -- same idempotent pattern as every other
    add_*_column() migration in this file, safe to call on every app startup.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(taxis)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    columns_to_add = {
        "last_known_zone_id": "INTEGER",
        "pending_zone_id": "INTEGER",
        "pending_zone_count": "INTEGER DEFAULT 0",
        "last_ping_at": "TEXT",
    }

    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE taxis ADD COLUMN {column_name} {column_type}")

    conn.commit()
    conn.close()

def add_zone_management_columns():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    columns_to_add = {
        "name": "TEXT",
        "active": "INTEGER DEFAULT 1",
    }

    for column_name, column_type in columns_to_add.items():
        try:
            cursor.execute(f"ALTER TABLE geofence_zones ADD COLUMN {column_name} {column_type}")
            conn.commit()
            print(f"{column_name} column added")
        except sqlite3.OperationalError:
            print(f"{column_name} column already exists")

    conn.close()

def add_zone_occupancy_table():
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS zone_occupancy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                taxi_id INTEGER NOT NULL,
                zone_id INTEGER NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                FOREIGN KEY (taxi_id) REFERENCES taxis(id),
                FOREIGN KEY (zone_id) REFERENCES geofence_zones(id)
            )
        """)
        conn.commit()
    finally:
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

def add_fare_column():
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(routes)")
        existing_columns = [row[1] for row in cursor.fetchall()]

        if "fare_per_passenger" not in existing_columns:
            cursor.execute(
                "ALTER TABLE routes ADD COLUMN fare_per_passenger REAL NOT NULL DEFAULT 0"
            )
            conn.commit()
            print("fare_per_passenger column added to routes.")
        else:
            print("fare_per_passenger column already exists -- no changes made.")
    finally:
        conn.close()

def add_last_logout_column():
    """Adds users.last_logout_at -- used for the 'Welcome back' greeting."""
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("ALTER TABLE users ADD COLUMN last_logout_at TEXT")
        conn.commit()
        print("last_logout_at column added.")
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()


def add_platform_support():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platforms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
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

    platform_layers = {
        "Platform 1": ["Straight Evaton", "Eastern road", "Zone 3 via Residensia",
                       "Zone 8 Smallfarm", "Zone 10/Zone 7"],
        "Platform 2": ["Zone 11/12/13/14", "Zone 16/17"],
        "Platform 3": ["Palm Springs Mall via Sporo", "Zone 28/GG",
                       "Boitumelo via extension 15 and Beverley Hills"],
    }

    for platform_name, layers in platform_layers.items():
        cursor.execute("SELECT id FROM platforms WHERE name = ?", (platform_name,))
        platform = cursor.fetchone()
        if platform:
            for layer_name in layers:
                cursor.execute("INSERT OR IGNORE INTO layers (platform_id, name) VALUES (?, ?)",
                               (platform["id"], layer_name))

    conn.commit()
    conn.close()

def add_phone_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        conn.commit()
        print("phone column added")
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_active_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN active INTEGER DEFAULT 1")
        conn.commit()
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_weekend_letter_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE taxis ADD COLUMN weekend_letter TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_prdp_expiry_column():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE taxis ADD COLUMN prdp_expiry DATE")
        conn.commit()
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def add_push_subscriptions_table():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subscription_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_trip_classification_columns():
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(trips)")
        existing_columns = [row[1] for row in cursor.fetchall()]

        if "route_type" not in existing_columns:
            cursor.execute(
                "ALTER TABLE trips ADD COLUMN route_type TEXT "
                "CHECK (route_type IN ('revenue', 'feeder'))"
            )
            print("route_type column added to trips.")
        else:
            print("route_type column already exists -- no changes made.")

        if "linked_trip_id" not in existing_columns:
            cursor.execute(
                "ALTER TABLE trips ADD COLUMN linked_trip_id  INTEGER "
                "REFERENCES trips(id)"
            )
            print("linked_trip_id column added to trips.")
        else:
            print("linked_trip_id column already exists -- no changes made.")

        conn.commit()
    finally:
        conn.close()

def add_passenger_counts_table():
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passenger_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL UNIQUE,
                date_started DATE,
                time_started TIME,
                date_ended DATE,
                time_ended TIME,
                final_in_count INTEGER DEFAULT 0,
                final_out_count INTEGER DEFAULT 0,
                final_net_occupancy INTEGER DEFAULT 0,
                FOREIGN KEY (trip_id) REFERENCES trips(id)
            )
        """)
        conn.commit()
        print("passenger_counts table ready.")
    finally:
        conn.close()

def add_crossings_table():
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crossings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                direction TEXT NOT NULL CHECK (direction IN ('IN', 'OUT')),
                track_id INTEGER,
                running_net INTEGER,
                FOREIGN KEY (trip_id) REFERENCES trips(id)
            )
        """)
        conn.commit()
        print("crossings table ready.")
    finally:
        conn.close()

def backup_database(db_path):
    """
    Makes a timestamped backup copy of the database using SQLIite's own
    online-backup method (safe even if another connection is reading).
    Returns the backup file's path.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found, refusing to back up: {db_path}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{stamp}"

    source = sqlite3.connect(db_path)
    try:
        target = sqlite3.connect(backup_path)
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()

    return backup_path

def add_gps_pings_table():
    """
    One row per GPS ping -- the trail a trip leaves behind.

    recorded_at = when the PHONE took the reading (used for gate crossings)
    received_at = when the SERVER got it (pings can arrive late after a dead spot)
    """
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gps_pings (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                taxi_id      INTEGER NOT NULL,
                lat          REAL NOT NULL CHECK (lat BETWEEN -90 AND 90),
                lon          REAL NOT NULL CHECK (lon BETWEEN -180 AND 180),
                recorded_at  DATETIME NOT NULL,
                received_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                accuracy_m   REAL CHECK (accuracy_m IS NULL OR accuracy_m >= 0),
                FOREIGN KEY (taxi_id) REFERENCES taxis(id)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_gps_pings_taxi_time
            ON gps_pings (taxi_id, recorded_at)
        """)
        conn.commit()
        print("gps_pings table ready.")
    finally:
        conn.close()

def extend_zone_type_check():
    """
    Rebuilds geofence_zones so zone_type also allows 'checkpoint'.
    SQLite cannot alter a CHECK constraint in place, so this follows the
    official rebuild procedure inside a single transaction.
    Safe to run more than once: it exts early if already applied.
    """
    db_path = get_db_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.isolation_level = None

    try:
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'geofence_zones'"
        ).fetchone()
        if row is None:
            raise RuntimeError("geofence_zones does not exist -- run the earlier migrations first.")
        original_sql = row[0]

        if "'checkpoint'" in original_sql:
            print("geofence_zones already allows 'checkpoint' -- nothing to do.")
            return

        check_pattern = re.compile(
               r"CHECK\s*\(\s*zone_type\s+IN\s*\([^)]*\)\s*\)", re.IGNORECASE
        )
        if not check_pattern.search(original_sql):
            raise RuntimeError(
                "Could not find the zone_type CHECK constraint in geofence_zone. "
                "Stopping without changing anything. Original definition:\n" + original_sql
            )

        new_sql = check_pattern.sub(
            "CHECK (zone_type IN ('rank', 'destination', 'checkpoint'))",
            original_sql,
            count=1,
        )
        new_sql = re.sub(
            r"^CREATE TABLE\s+(IF NOT EXISTS\s+)?[\"`\[]?geofence_zones[\"`\]]?",
            "CREATE TABLE geofence_zones_new",
            new_sql,
            count=1,
            flags=re.IGNORECASE,
        )
        if "geofence_zones_new" not in new_sql:
            raise RuntimeError("Could not rename the table in the CREATE statement. Stopping.")

        columns = [col[1] for col in conn.execute("PRAGMA table_info(geofence_zones)")]
        column_list = ", ".join(f'"{name}"' for name in columns)

        extra_objects = [
            r[0] for r in conn.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type IN ('index', 'trigger') AND tbl_name = 'geofence_zones' "
                "AND sql IS NOT NULL"
            )
        ]

        try:
            seq_row = conn.execute(
                "SELECT seq FROM sqlite_sequence WHERE name = 'geofence_zones'"
            ).fetchone()
            old_seq = seq_row[0] if seq_row else None
        except sqlite3.OperationalError:
            old_seq = None

        referencing_tables = [
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND sql LIKE '%REFERENCES geofence_zones%'"
            )
        ]

        backup_path = backup_database(db_path)
        print(f"Backup written: {backup_path}")

        conn.execute("PRAGMA foreign_key = OFF")
        conn.execute("BEGIN")
        try:
            conn.execute(new_sql)
            conn.execute(
                f"INSERT INTO geofence_zones_new ({column_list}) "
                f"SELECT {column_list} FROM geofence_zones"
            )

            old_count = conn.execute("SELECT COUNT(*) FROM geofence_zones").fetchone()[0]
            new_count = conn.execute("SELECT COUNT(*) FROM geofence_zones_new").fetchone()[0]
            if old_count != new_count:
                raise RuntimeError(f"Row count mismatch: {old_count} old vs {new_count} new.")

            conn.execute("DROP TABLE geofence_zones")
            conn.execute("ALTER TABLE geofence_zones_new RENAME TO geofence_zones")

            for sql in extra_objects:
                conn.execute(sql)

            if old_seq is not None:
                conn.execute(
                    "UPDATE sqlite_sequence SET seq = MAX(seq, ?) WHERE name = 'geofence_zones'",
                    (old_seq,),
                )

            for table in ["geofence_zones"] + referencing_tables:
                problems = conn.execute(f'PRAGMA foreign_key_check("{table}")').fetchall()
                if problems:
                    raise RuntimeError(f"Foreign key problems in {table} after rebuild: {problems}")

            conn.execute("COMMIT")
            print(f"geofence_zones rebuilt: {new_count} rows kept, 'checkpoint' now allowed.")
        except Exception:
            conn.execute("ROLLBACK")
            print("Rebuild failed -- rolled back. Database is unchanged.")
            raise
    finally:
        conn.close()

def add_route_checkpoints_table():
    """
    Create route_checkpoints: the ordered gates along a route.

    boarding_fare = what a passenger pays if they board AFTER passing
    this gate. NULL means no boarding is expected after this gate --
    any boarding there is flagged for review, never priced.
    """
    conn = sqlite3.connect(get_db_path())
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS route_checkpoints (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id      INTEGER NOT NULL,
                zone_id       INTEGER NOT NULL,
                sequence      INTEGER NOT NULL CHECK (sequence >= 1),
                boarding_fare REAL CHECK (boarding_fare IS NULL OR boarding_fare > 0),
                created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (route_id) REFERENCES routes(id),
                FOREIGN KEY (zone_id)  REFERENCES geofence_zones(id),
                UNIQUE (route_id, sequence),
                UNIQUE (route_id, zone_id)
            )
        """)
        conn.commit()
        print("route_checkpoints table ready.")
    finally:
        conn.close()


if __name__ == "__main__":

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
    add_phone_column()
    add_active_column()
    add_weekend_letter_column()
    add_prdp_expiry_column()
    add_push_subscriptions_table()
    add_geofencing_columns()
    add_zone_management_columns()
    add_zone_occupancy_table()
    add_fare_column()
    add_trip_classification_columns()
    add_passenger_counts_table()
    add_crossings_table()
    add_route_checkpoints_table()
    add_last_logout_column()
    add_gps_pings_table()
