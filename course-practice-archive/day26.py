import requests
from bs4 import BeautifulSoup
import pandas as pd

url= "https://books.toscrape.com"
headers= {
    "User-Agent":"Mozilla/5.0(Windoes NT 10.0; Win64; x64) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Success")
else:
    print(f"Failed: {response.status_code}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    print("Page loaded successfully")
    print(soup.find("title").text)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

print("Scrape complete")
