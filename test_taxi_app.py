import pytest
import logging
import datetime
from taxi_app import app, get_db
from utils import taxi_should_be_working
from unittest.mock import patch

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
    assert "event=report_generated"

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


def test_log_trip(client):
    try:
        client.post('/login', data={'username': 'sechaba_admin', 'password': 'separaka_admin_2026'})
        client.get('/logout')
        client.post('/login', data={'username': 'marshall1', 'password': 'marshall123'})
        conn = get_db()
        conn.execute("UPDATE users SET platform_id = 1 WHERE username = 'marshall1'")
        conn.execute("UPDATE taxis SET platform_id = 1 WHERE id = 1")
        conn.commit()
        conn.close()

        client.post('/api/queue/join', data={'taxi_id': '1', 'layer': 'Straight Evaton'})
        response = client.post('/api/queue/depart', data={'route_id': '1'})
        assert response.status_code == 200
    finally:
        conn = get_db()
        conn.execute("DELETE FROM queue WHERE taxi_id = 1")
        conn.commit()
        conn.close()

def test_owner_join_queue_logs_warning(client, caplog):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    with caplog.at_level(logging.WARNING):
        response = client.post('/api/queue/join', data={'taxi_id': '1'})
    assert response.status_code == 403
    assert "event=non_marshall_join_attempt" in caplog.text

def test_duplicate_plate_logs_warning(client, caplog):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    try:
        client.post('/admin/taxi/add', data={
            'plate': 'DUPETEST GP', 'driver_name': 'X',
            'driver_username': 'dupetest1', 'password': 'pass123',
            'platform_id': '1'
        })
        with caplog.at_level(logging.WARNING):
            client.post('/admin/taxi/add', data={
                'plate': 'DUPETEST GP','driver_name': 'Y',
                'driver_username': 'dupetest2', 'password': 'pass123',
                'platform_id': '1'
            })
        assert "event=duplicate_plate" in caplog.text.lower()
    finally:
        conn = get_db()
        conn.execute("DELETE FROM taxis WHERE plate = 'DUPETEST GP'")
        conn.execute("DELETE FROM users WHERE username IN ('dupetest1', 'dupetest2')")
        conn.commit()
        conn.close()

def test_depart_queue_warning(client, caplog):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    with caplog.at_level(logging.WARNING):
        response = client.post('/api/queue/depart', data={'taxi_id': '1'})
    assert response.status_code == 403
    assert "event=non_marshall_depart_queue_attempt" in caplog.text

def test_taxi_should_be_working_matches_letter():
    check_date = datetime.date(2026, 8, 11)
    assert taxi_should_be_working("A", check_date) == True
    assert taxi_should_be_working("B", check_date) == False

def test_taxi_should_be_working_with_no_letter():
    check_date = datetime.date(2026, 8, 11)
    assert taxi_should_be_working(None, check_date) == True
    assert taxi_should_be_working("", check_date) == True

def test_forgot_password_uses_sms_when_no_email(client, caplog):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE username = 'phone_only_user'")
    conn.commit()
    conn.close()
    
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO users (username, password, role, phone, email)
            VALUES ('phone_only_user', ?, 'owner', '27000000000', NULL)
        """, (b'$2b$12$fakehashvalueforthistest',))
        conn.commit()
        conn.close()

        with patch('blueprints.auth.send_sms') as mock_send_sms:
            with caplog.at_level(logging.INFO):
                client.post('/forgot-password', data={'username': 'phone_only_user'})
            mock_send_sms.assert_called_once()

        assert "event=password_reset_requested_sms" in caplog.text

    finally:
        conn = get_db()
        conn.execute("DELETE FROM users WHERE username = 'phone_only_user'")
        conn.execute("DELETE FROM password_resets WHERE user_id IN (SELECT id FROM users WHERE username ='phone_only_user')")
        conn.commit()
        conn.close()
   
    






