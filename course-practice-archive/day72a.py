import os
import requests
from dotenv import load_dotenv

load_dotenv()

TEST_API_KEY = os.environ.get("TEST_API_KEY")
TEST_API_KEY = "abc123"

print(TEST_API_KEY)
try:
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    data = response.json()
    print(data["rates"]["ZAR"])
    response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
    response.raise_for_status()
    print("True")
except requests.exceptions.Timeout:
    print("SMS provider took too long to respond")
except requests.exceptions.RequestException as e:
    print(f"SMS failed: {e}")
