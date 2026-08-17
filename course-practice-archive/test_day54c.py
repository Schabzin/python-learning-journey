from day54b_app import app, get_db, create_token
import os, pytest

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
    os.remove(TEST_DB)
    try:
        os.remove(TEST_DB)
    except (FileNotFoundError, PermissionError):
        pass

def test_duplicate_item(client):
    client.post("/items", json={"name": "Calculator", "price": 258.90, "category": "Stationery"})
    response = client.post("/items", json={"name": "Calculator", "price": 258.90, "category": "Stationery"})
    assert response.status_code == 400

def test_empty_name(client):
    response = client.post("/items", json={"name": "", "price": 258.90, "category": "Stationery"})
    assert response.status_code == 400

def test_full_lifecycle(client):
    response = client.post("/items", json={"name": "Stapler", "price": 26.60, "category": "Stationery"})
    print(response.status_code, response.get_json())
    assert response.status_code == 201
    item_id = response.get_json()["id"]

    token = create_token("sechaba", "owner")
    response = client.get(f"/items/{item_id}", headers={"Authorization": token})
    assert response.status_code == 200
    assert response.get_json()["name"] == "Stapler"

    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.get_json()["items"]) == 1

def test_not_found(client):
    token = create_token("sechaba", "owner")
    response = client.get("/items/9999", headers={"Authorization": token})
    assert response.status_code == 404