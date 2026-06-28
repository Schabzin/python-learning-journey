import pytest
from taxi_app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client
        
def test_login(client):
    response = client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    assert response.status_code == 302
    assert response.location == '/dashboard'

def test_dashboard_requires_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert response.location == '/login'

def test_log_trip(client):
    client.post('/login', data={'username': 'marshall1', 'password': 'marshall123'})
    response = client.post('/api/trips', json={'taxi_id': 1, 'route_id': 1})
    assert response.status_code == 201

def test_update_target(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.post('/api/target', data={'taxi_id': '1', 'number': '900'})
    assert response.status_code == 302


