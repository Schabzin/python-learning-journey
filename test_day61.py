import os
import sqlite3
import pytest
from taxi_app import app, get_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def get_db():
    if os.path.exists("/data"):
        conn = sqlite3.connect("/data/taxi.db")
    else:
        conn = sqlite3.connect("taxi.db")
        conn.row_factory = sqlite3.Row
        return conn
    
def get_db_path():
    if os.path.exists("/data"):
        return "/data/taxi.db"
    return '/taxi.db'

def test_log_trip(client):
    client.post('/login', data={'username': 'marshall1', 'password': 'marshall123'})
    response = client.post('/api/trips', json={'taxi_id': 1, 'route_id': 1})
    assert response.status_code == 201

def test_add_taxi(client):
    client.post('/login', data={'username': 'chahane', 'password': 'kalikeng2026'})
    response = client.post('/admin/taxi/add', data={
        'plate': 'TEST123 GP',
        'driver_name': 'TestDriver',
        'driver_username': 'testdriver99',
        'password': 'test999'
    })
    assert response.status_code == 302

    conn = get_db()
    conn.execute("DELETE FROM taxis WHERE plate = ?", ('TEST123 GP',))
    conn.execute("DELETE FROM users WHERE username = ?", ('testdriver99',))
    conn.commit()
    conn.close()