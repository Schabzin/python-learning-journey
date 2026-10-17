"""
seed_demo.py - creates the Separaka DEMO owner, marshall, drivers and taxis.
Run by hand only: python seed_demo.py
Never imported by the app. Never run on startup.
"""
import os
import sqlite3
import getpass
import bcrypt
from datetime import date, datetime, timedelta
from utils import get_db_path
from setup_taxi_db import backup_database

DEMO_OWNER = "demo_owner"
DEMO_MARSHALL = "demo_marshall"
DEMO_DRIVERS = ["demo_driver1", "demo_driver2", "demo_driver3"]
DEMO_PLATFORM = "DEMO Platform"
DEMO_RANK = "DEMO Rank (Separaka sample)"
DEMO_LAYER = "DEMO Layer A"
DEMO_ROUTE = "DEMO Route: Rank to Town"
DEMO_FARE = 20.0

TAXIS = [
    {"plate": "DEMO 001 GP", "driver": "demo_driver1", "driver_name": "Demo Driver One",
     "current_km": 152300, "last_service_km": 145000, "next_service_km": 160000,
     "prdp_days": 300},
    {"plate": "DEMO 002 GP", "driver": "demo_driver2", "driver_name": "Demo Driver Two",
     "current_km": 98700, "last_service_km": 88000, "next_service_km": 98000,
     "prdp_days": 200},
    {"plate": "DEMO 003 GP", "driver": "demo_driver3", "driver_name": "Demo Driver Three",
     "current_km": 61200, "last_service_km": 60000, "next_service_km": 70000,
     "prdp_days": 10},
]

class SeedError(Exception):
    """Raised when the seed must stop before touching anything."""

def ask_password(label):
    first = getpass.getpass(f"Password for {label}: ")
    second = getpass.getpass("Type it again: ")
    if first != second:
        raise SeedError(f"Password for {label} do not match.")
    if len(first) < 8:
        raise SeedError(f"Password for {label} must be at least 8 characters.")
    return bcrypt.hashpw(first.encode(), bcrypt.gensalt())

def already_seeded(conn):
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", (DEMO_OWNER,)
    ).fetchone()
    return row is not None

def insert(conn, sql, params):
    cursor = conn.execute(sql, params)
    return cursor.lastrowid

def seed(conn, owner_hash, marshall_hash, driver_hash):
    today = date.today()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    paid_until = (today + timedelta(days=365)).isoformat()

    platform_id = insert(conn,
        "INSERT INTO platforms (name, rank_name) VALUES (?, ?)",
        (DEMO_PLATFORM, DEMO_RANK))

    insert(conn,
        "INSERT INTO layers (platform_id, name) VALUES (?, ?)",
        (platform_id, DEMO_LAYER))

    route_id = insert(conn,
        "INSERT INTO routes (name, platform_id, fare_per_passenger) VALUES (?, ?, ?)",
        (DEMO_ROUTE, platform_id, DEMO_FARE))

    user_sql = ("INSERT INTO users (username, password, role, created_at, "
                "paid_until, platform_id, active) VALUES (?, ?, ?, ?, ?, ?, 1)")

    owner_id = insert(conn, user_sql,
        (DEMO_OWNER, owner_hash, "owner", now, paid_until, platform_id))
    marshall_id = insert(conn, user_sql,
        (DEMO_MARSHALL, marshall_hash, "marshall", now, paid_until, platform_id))
    for username in DEMO_DRIVERS:
        insert(conn, user_sql,
            (username, driver_hash, "driver", now, paid_until, platform_id))

    taxi_sql = ("INSERT INTO taxis (plate, driver_name, driver_phone, route, "
                "current_km, last_service_km, next_service_km, last_service_date, "
                "status, owner_id, driver_username, platform_id, weekend_letter, "
                "prdp_expiry, ab_letter) "
                "VALUES (?, ?, NULL, ?, ?, ?, ?, ?, 'active', ?, ?, ?, 'A', ?, 'A')")

    taxi_ids = {}
    for t in TAXIS:
        last_service = (today - timedelta(days=40)).isoformat()
        prdp_expiry = (today + timedelta(days=t["prdp_days"])).isoformat()
        taxi_ids[t["plate"]] = insert(conn, taxi_sql,
            (t["plate"], t["driver_name"], DEMO_ROUTE,
             t["current_km"], t["last_service_km"], t["next_service_km"],
             last_service, owner_id, t["driver"], platform_id, prdp_expiry))
        

    return {"platform_id": platform_id, "route_id": route_id,
            "owner_id": owner_id, "marshall_id": marshall_id,
            "taxi_ids": taxi_ids}

def main():
    db_path = get_db_path()
    print(f"Database: {db_path}")

    if not os.path.exists(db_path):
        raise SeedError(f"No database at {db_path}. Wrong path?")

    conn = sqlite3.connect(db_path)
    try:
        if already_seeded(conn):
            raise SeedError(f"{DEMO_OWNER} already exists. Nothing done.")

        owner_hash = ask_password(DEMO_OWNER)
        marshall_hash = ask_password(DEMO_MARSHALL)
        driver_hash = ask_password("all demo drivers")

        backup_path = backup_database(db_path)
        print(f"Backup written: {backup_path}")

        with conn:
            ids = seed(conn, owner_hash, marshall_hash, driver_hash)

        print(f"Demo platform id: {ids['platform_id']}")
        print(f"Demo owner id:    {ids['owner_id']}")
        for plate, taxi_id in ids["taxi_ids"].items():
            print(f"  {plate} -> taxi id {taxi_id}")
        print("Demo seed complete.")
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        main()
    except SeedError as e:
        print(f"STOPPED: {e}")