"""
test_ping_route.py
Proves /api/taxi/ping turns away anyone who is not a logged-in driver.
The tests in this lesson never reach the database.
"""
import pytest
import sqlite3
from taxi_app import app

PING = {"lat": -26.68, "lon": 27.83}

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def log_in_as(client, username, role):
    """Pretend this person logged in."""
    with client.session_transaction() as sess:
        sess["user"] = username
        sess["role"] = role

def test_no_login_gets_401(client):
    response = client.post("/api/taxi/ping", json=PING)

    assert response.status_code == 401
    assert response.get_json()["error"] == "Login required"

@pytest.mark.parametrize("role", ["owner", "marshall", "admin", None])
def test_non_driver_gets_403(client, role):
    log_in_as(client, "someone", role)

    response = client.post("/api/taxi/ping", json=PING)

    assert response.status_code == 403
    assert response.get_json()["error"] == "Only drivers can send pings"



def pings_in(path):
    """Every saved ping, as (plate, lat, lon)."""
    conn = sqlite3.connect(path)
    try:
        return conn.execute(
            """SELECT t.plate, p.lat, p.lon
               FROM gps_pings p JOIN taxis t ON t.id = p.taxi_id
               ORDER BY p.id"""
        ).fetchall()
    finally:
        conn.close()

def test_driver_without_taxi_gets_403(client, test_db):
    log_in_as(client, "no_taxi_driver", "driver")

    response = client.post("/api/taxi/ping", json=PING)

    assert response.status_code == 403
    assert response.get_json()["error"] == "No taxi assigned to this driver"
    assert pings_in(test_db) == []

def test_driver_ping_is_saved(client, test_db):
    log_in_as(client, "tester", "driver")

    response = client.post("/api/taxi/ping", json=PING)

    assert response.status_code == 200
    assert pings_in(test_db) == [("TEST01GP", -26.68, 27.83)]

def test_cannot_ping_for_another_taxi(client, test_db):
    conn = sqlite3.connect(test_db)
    other_id = conn.execute(
        "SELECT id FROM taxis WHERE plate = 'OTHER2GP'").fetchone()[0]
    conn.close()
    log_in_as(client, "tester", "driver")

    response = client.post("/api/taxi/ping", json=dict(PING, taxi_id=other_id))

    assert response.status_code == 200
    assert pings_in(test_db) == [("TEST01GP", -26.68, 27.83)]
    

