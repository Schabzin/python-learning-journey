import requests

response = requests.get("https://jsonplaceholder.typicode.com/users")
print(response.status_code)

data = response.json()
print(f"Total users returned: {len(data)}")

for user in data:
    print(f"{user['name']} - {user['email']}")

response2 = requests.get("https://jsonplaceholder.typicode.com/users/1")
user1 = response2.json()
print(user1)
print("API Session 1 complete")