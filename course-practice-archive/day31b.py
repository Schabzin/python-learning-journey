import requests

url = f"https://openexchangerates.org/api/latest.json"
params = {"app_id": "410c5fb560e74ecc8fdc03cc9d47d757"}

try:
    response = requests.get(url, params=params)
    print(response.status_code)
    data = response.json()
    print(f"Base currency: {data['base']}")
    print(f"ZAR rate: {data['rates']['ZAR']}")
    print(f"GBP rate: {data['rates']['GBP']}")
    print(f"EUR rate: {data['rates']['EUR']}")
    print("Exchange rates retrieved!")
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")