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

def test_protected_route(client):
    response = client.get("/items/1")
    assert response.status_code == 401
    client.post("/items",
        json={"name": "Pen", "price": 5.50, "category": "Stationery"}
    )

    token = create_token("sechaba", "owner")
    response = client.get("/items/1",
        headers={"Authorization": token}
    )
    assert response.status_code == 200
 
def test_create_and_retrieve(client):
    response = client.post("/items",
        json={"name": "A4 Paper", "price": 89.99, "category": 'Stationery'}
    )
    assert response.status_code == 201
    item_id = response.get_json()["id"]
    token = create_token("sechaba", "owner")
    response = client.get(f"/items/{item_id}",
        headers={"Authorization": token}
    )
    print(response.get_json())
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "A4 Paper"


def test_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == 401


