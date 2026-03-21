import requests

response = requests.get ("https://api.exchangerate-api.com/v4/latest/ZAR")
data = response.json()

try:
    print("=" * 40)
    print("  KALIKENG CURRENCY CHECKER ")
    print("  Rates based on 1 South African Rand ")
    print("=" * 40)
    print(f"USD (Dollar)           : {data['rates']['USD']:.4f}")
    print(f"GBP (British Pound)    : {data['rates']['GBP']:.4f}")
    print(f"EUR (Euro)             : {data['rates']['EUR']:.4f}")
    print(f"BWP (Botswana Pula)    : {data['rates']['BWP']:.4f}")
    print("=" * 40)
except Exception:
    print("No internet connection. Please try again.")
