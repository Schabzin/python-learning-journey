import pytest
from day54_app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_get_item(client):
    response = client.get("/items")
    assert response.status_code == 200
    data = response.get_json()
    assert "items" in data

def test_create_item(client):
    response = client.post("/items",
        json={"name": "Ruler"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Item created"

def test_missing_fields(client):
    response = client.post("/items", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == 404