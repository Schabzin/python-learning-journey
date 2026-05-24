
import requests

login_response = requests.post("http://127.0.0.1:5000/api/login",
    json={"username": "sechaba", "password": "kalikeng"})

print("Login status:", login_response.status_code)
print("Login response:", login_response.text)

data = login_response.json()
token = data["token"]

profile_response = requests.get("http://127.0.0.1:5000/api/profile",
    headers={"Authorization": f"Bearer {token}"})

print("Profile:", profile_response.json())