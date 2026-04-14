import requests

url = "https://jsonplaceholder.typicode.com/posts"
params = {"_limit": 5}

try:
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        print("Success")
        for post in data:
            title = post.get("title", "Unknown")
            body = post.get("body", "No body")
            print(f"UserID: {post['userId']} | Title: {title[:50]} | Body: {body[:80]}")
    elif response.status_code == 404:
        print("Not found")
    elif response.status_code == 500:
        print("Server error - try again later")

    response2 = requests.get("https://jsonplaceholder.typicode.com/invalid")
    if response2.status_code == 404:
        print("404 - Page not found")

except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")