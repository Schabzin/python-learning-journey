"""
test_ping_route.py
Proves /api/taxi/ping turns away anyone who is not a logged-in driver.
The tests in this lesson never reach the database.
"""
import pytest

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

