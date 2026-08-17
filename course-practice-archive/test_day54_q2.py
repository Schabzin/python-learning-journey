import pytest, os
from test_day54_app import app, get_db, create_token


TEST_DB = "test_app.db"

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["DATABASE"] = TEST_DB
    with app.test_client() as client:
        with app.app_context():
            conn = get_db()
            conn.close()
        yield client

    try:
        os.remove(TEST_DB)
    except (FileNotFoundError, PermissionError ):
        pass

def test_get_products(client):
    response = client.get("/products")
    assert response.status_code == 200

def test_create_product(client):
    response = client.post("/products",
            json={"name":"Ruler", "price": 1.80, "category": "Stationery"})
    assert response.status_code == 201

def test_missing_fields(client):
    response = client.post("/products", json={})
    assert response.status_code == 400

def test_not_found(client):
    token = create_token("sechaba", "owner")
    response = client.get("/products/9999",
        headers={"Authorization": token})
    assert response.status_code == 404

def test_protected_route(client):
    response = client.get("/products/1")
    assert response.status_code == 401

def test_duplicate_product(client):
    client.post("/products",
        json={"name": "Ruler", "price": 1.80, "category": "Stationery"})
    response = client.post("/products",
            json={"name": "Ruler", "price": 1.80, "category": "Stationery"})
    assert response.status_code == 201
    





 

