"""
test_depart_race.py -- Day 113 Session 1: prove depart_queue() is race-safe.

This script talks to your LIVE running server over HTTP -- it does not import
your app. Setup inserts one test taxi directly into 'waiting' status in the
queue table, bypassing join_queue() (which currently can't run because of the
separate 'layer' column mismatch -- not today's problem, flagged for later).
Then it fires two near-simultaneous POST /api/queue/depart calls as the same
marshall and checks that exactly one succeeds.

BEFORE RUNNING:
1. Start your Flask add first, in its own terminal (however you normally run it).
2. Set DB_PATH below to whatever path your db.py / get_db_path() actually uses --
   open that file and copy the exact tring, don't guess it.
3. pip install requests    (if you don't already have it)
"""

import sqlite3
import threading
import requests

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = r"C:\Users\Sechaba\Desktop\python\taxi.db"

MARSHALL_USERNAME = "marshall1"
MARSHALL_PASSWORD = "marshall123"

def setup_test_data():
    """Find marshall1's platform, a real taxi and a real route, and put that
    taxi into 'waiting' status in the queue -- directly, bypassing join_queue()."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, platform_id FROM users WHERE username = ?", (MARSHALL_USERNAME,))
    marshall = cursor.fetchone()
    if marshall is None:
        raise RuntimeError(f"No user '{MARSHALL_USERNAME}' found -- check DB_PATH and the username")
    if marshall["platform_id"] is None:
        raise RuntimeError(
            f"'{MARSHALL_USERNAME}' has no platform_id set. Assign one first, e.g.:\n"
            "  UPDATE users SET platform_id = 1 WHERE username = 'marshall1';"
        )
    platform_id = marshall["platform_id"]

    cursor.execute("SELECT id FROM taxis LIMIT 1")
    taxi = cursor.fetchone()
    if taxi is None:
        raise RuntimeError("No taxis exist in the taxis table -- add at least one first")
    taxi_id = taxi["id"]

    cursor.execute("SELECT id FROM routes LIMIT 1")
    route = cursor.fetchone()
    if route is None:
        cursor.execute("INSERT INTO routes (name) VALUES ('Test Route')")
        conn.commit()
        route_id = cursor.lastrowid
        print(f"Created a test route (id={route_id}) -- none existed")
    else:
        route_id = route["id"]

    cursor.execute("DELETE FROM queue WHERE platform_id = ? AND status = 'waiting'", (platform_id,))

    cursor.execute(
        "INSERT INTO queue (taxi_id, platform_id, position, status) VALUES (?, ?, 1, 'waiting')",
        (taxi_id, platform_id),
    )
    conn.commit()
    conn.close()

    print(f"Test data ready: taxi_id={taxi_id}, platform_id={platform_id}, route_id={route_id}")
    return route_id


def login():
    """Log in as marshall1 in a fresh session, return that session carrying
    the login cookie -- each thread needs its OWN session, not a shared one."""
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/login",
        data={"username": MARSHALL_USERNAME, "password": MARSHALL_PASSWORD},
    )
    if "Invalid credentials" in response.text:
        raise RuntimeError("Login failed -- check MARSHALL_USERNAME/MARSHALL_PASSWORD")
    return session


def race_depart(route_id, results, index, barrier):
    """Runs in its own thread. Blocks at the barrier so both threads fire
    their POST at the same instant, then records what came back."""
    session = login()
    barrier.wait()  
    response = session.post(
        f"{BASE_URL}/api/queue/depart",
        data={"route_id": route_id},
    )
    results[index] = (response.status_code, response.json())

def setup_join_test_data():
    """Unlike depart's setup, we want the queue EMPTY for this taxi --
    proving join_queue()'s race guard means starting with nothing to guard
    against yet, then having two threads try to create the same row at once."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT platform_id FROM users WHERE username = ?", (MARSHALL_USERNAME,))
    marshall = cursor.fetchone()
    if marshall is None or marshall["platform_id"] is None:
        raise RuntimeError(f"'{MARSHALL_USERNAME}' has no platform_id set -- fix that first")
    platform_id = marshall["platform_id"]

    cursor.execute("SELECT id FROM taxis LIMIT 1")
    taxi = cursor.fetchone()
    if taxi is None:
        raise RuntimeError("No taxis exist in the taxis table -- add at least one first")
    taxi_id = taxi["id"]

    cursor.execute("DELETE FROM queue WHERE taxi_id = ? AND status = 'waiting'", (taxi_id,))
    conn.commit()
    conn.close()

    print(f"Join race test data ready: taxi_id={taxi_id}, platform_id={platform_id}")
    return taxi_id

def race_join(taxi_id, layer, results, index, barrier):
    """Runs in its own thread. Blocks at the barrier so both threads fire
    their POST at the same instant, then records what came back."""
    session = login()
    barrier.wait()
    response = session.post(
        f"{BASE_URL}/api/queue/join",
        data={"taxi_id": taxi_id, "layer": layer},
        allow_redirects=False,
    )
    body = response.json() if response.status_code == 200 else None
    results[index] = (response.status_code, body)

def run_join_race_test():
    taxi_id = setup_join_test_data()
    layer = "Zone 3 via Residensia"

    results = [None, None]
    barrier = threading.Barrier(2)

    thread_a = threading.Thread(target=race_join, args=(taxi_id, layer, results, 0, barrier))
    thread_b = threading.Thread(target=race_join, args=(taxi_id, layer, results, 1, barrier))

    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    print("\n--- Join Race Results ---")
    for i, (status, body) in enumerate(results):
        print(f"Request {i}: status={status} body={body}")

    statuses = sorted(r[0] for r in results)
    if statuses == [200, 302]:
        print("\nPASS: exactly one join succeeded, the other was correctly redirected (blocked).")
    else:
        print("f\nFAIL: expected [200, 302], got {statuses} -- the race condition is not fixed.")


def run_race_test():
    route_id = setup_test_data()

    results = [None, None]
    barrier = threading.Barrier(2)  

    thread_a = threading.Thread(target=race_depart, args=(route_id, results, 0, barrier))
    thread_b = threading.Thread(target=race_depart, args=(route_id, results, 1, barrier))

    thread_a.start()
    thread_b.start()
    thread_a.join()
    thread_b.join()

    print("\n--- Results ---")
    for i, (status, body) in enumerate(results):
        print(f"Request {i}: status={status} body={body}")

    statuses = sorted(r[0] for r in results)
    if statuses == [200, 409] or statuses == [200, 400]:
        print("\nPASS: exactly one depart succeeded, the other was correctly rejected.")
    else:
        print(f"\nFAIL: expected one 200 and one rejection, got {statuses} -- the race condition is not fixed.")


if __name__ == "__main__":
    run_race_test()
    run_join_race_test()