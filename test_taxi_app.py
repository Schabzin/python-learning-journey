import pytest
from taxi_app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client
        
def test_log_trip_success(client):
    login_response = client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    assert login_response.status_code == 302

def test_log_trip_success(client):
    response = client.post('/api/trips', json={'taxi_id': 1, 'route_id': 1})
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Trip logged'
