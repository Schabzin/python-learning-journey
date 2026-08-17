import logging
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import re

logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("kaliekng_sytem.log"),
        logging.StreamHandler()
    ]
)

all_books = []

for page in range(1, 4):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")

    books = soup.find_all("article", class_="product_pod")
    for book in books:
        title = book.find("h3").find("a")["title"]
        price = book.find("p", class_="price_color").text
        all_books.append({"title": title, "price": price})
    time.sleep(1)
    logging.info(f"Scraped page {page} - {len(books)} books found")

df = pd.DataFrame(all_books)
df["clean_price"] = df["price"].astype(str).str.replace(r"[^\d.]", "", regex=True)
small= df[df["clean_price"].astype(float) < 20]
logging.info(f"Total books scraped: {len(df)} - After filtering: {len(small)}")
df.to_csv("kalikeng_affordable_books.csv", index=False)
print("Scraper complete!")