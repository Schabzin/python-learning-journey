
import requests


login = requests.post("http://127.0.0.1:5000/api/login",
    json={"username": "newuser", "password": "test123"})
print("Login:", login.status_code)

token = login.json()["token"]

profile = requests.get("http://127.0.0.1:5000/api/profile",
    headers={"Authorization": f"Bearer {token}"})
print("Profile:", profile.json())
