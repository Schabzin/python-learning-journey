import pytest
from taxi_app import app
from test_day64 import describe_km_status

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_login_valid_credentials(client):
    response = client.post("/login", data={'username': 'chahane', 'password': 'kalikeng2026'})
    assert response.status_code == 302
    assert response.location == '/dashboard'

def test_login_wrong_password(client):
    response = client.post("/login", data={'username': 'chahane', 'password': 'wrongpassword'})
    assert response.status_code == 302
    assert response.location == '/login'

@pytest.mark.parametrize("current_km, next_service_km, expected", [
    (145000, 140000, "Overdue for service"),
    (139600, 140000, "Service due soon"),
    (120000, 140000, "Service not due yet"),
])
def test_describe_km_status(current_km, next_service_km, expected):
    result = describe_km_status(current_km, next_service_km)
    assert result == expected