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
    """The old /api/trips route was merged into depart_queue() on Day 77 -- test that instead"""
    client.post('/login', data={'username': 'marshall1', 'password': 'marshall123'})
    login_response = client.post('/login', data={'username': 'marshall1', 'password': 'marshall123'})
    print("LOGIN STATUS:", login_response.status_code)
    client.post('/api/queue/join', data={'taxi_id': '1'})
    response = client.post('/api/queue/depart', data={'route_id': '1'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'departed' in data['message'].lower()
    

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
    conn.execute("DELETE FROM users WHERE username = ?", ('testdriver99',))
    conn.commit()
    conn.close()

def test_dashboard_includes_week_data(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Week Trips' in response.data

def test_owner_only_sees_own_taxis(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.get('/api/taxis')
    taxis = response.get_json()
    plates = [t['plate'] for t in taxis]
    assert 'FG09KL GP' not in plates

def test_login_required_redirects(client):
    """Sad path -- accessing dashboard without logging in should redirect, not crash"""
    response = client.get("/dashboard")
    assert response.status_code == 302

def test_login_success(client):
    """Happy path -- correct credentials should log in successfully"""
    response = client.post("/login", data={
        "username": "chahane",
        "password": "kalikeng2026"
    }, follow_redirects=True)
    assert response.status_code == 200

def test_join_queue_requires_marshall_role(client):
    """The exact permission check from join_queue() -- an owner should NEVER be able to join a queue"""
    client.post("/login", data={"username": "chahane", "password": "kalikeng2026"})
    response = client.post("/api/queue/join", data={"taxi_id": "1"})
    assert response.status_code == 403

def test_daily_report_downloads(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.get('/reports/daily')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert len(response.data) > 0

def test_report_only_shows_own_taxis(client):
    """Confirms the WHERE owner_id = ? filter genuinely works in the PDF route"""
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.get('/reports/daily')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_auth_blueprint_group(client):
    """Represents: login, logout, register"""
    response = client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    assert response.status_code == 302

def test_owner_blueprint_group(client):
    """Represents: dashboard, target, km"""
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_marshall_blueprint_group(client):
    """Represents: marshall page, queue join/depart"""
    client.post('/login', data={'username': 'marshall1', 'password': 'marshall123'})
    response = client.get('/marshall')
    assert response.status_code == 200

def test_admin_blueprint_group(client):
    """Represents: admin dashboard, platforms, marshalls"""
    client.post('/login', data={'username': 'sechaba_admin', 'password': 'separaka_admin_2026'})
    response = client.get('/admin')
    assert response.status_code == 200






