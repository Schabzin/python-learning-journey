import time
import requests
from bs4 import BeautifulSoup

for page in range(1, 6):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    headers = {
        "User-Agent": "Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup= BeautifulSoup(response.text, "lxml")
    print(f"Scraped page {page}")
    time.sleep(2)

print("Done!")