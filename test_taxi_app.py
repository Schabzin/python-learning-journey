import pytest
from taxi_app import app, get_db

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

def test_add_taxi(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.post('/admin/taxi/add', data={
        'plate': 'TEST123 GP',
        'driver_name': 'TestDriver',
        'driver_username': 'testdriver99',
        'password': 'testpass123'
    })
    assert response.status_code == 302

    conn = get_db()
    conn.execute("DELETE FROM taxis WHERE plate = ?", ('TEST123 GP',))
    conn.execute("DELETE FROM users WHERE username = ?", ('testdiver99',))
    conn.commit()
    conn.close()

def test_dashboard_includes_week_data(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Week Trips' in response.data






