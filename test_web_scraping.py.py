import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

all_books = []

for page in range(1, 3):
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup= BeautifulSoup(response.text, "lxml")

    books = soup.find_all("article", class_="product_pod")
    for book in books:
        title=book.find("h3").find("a")["title"]
        price=book.find("p", class_= "price_color").text
        all_books.append({"title": title, "price": price})

    time.sleep(1)

df= pd.DataFrame(all_books)
print(df)
print(f"Total books scraped: {len(all_books)}")
df.to_csv("test_books.csv", index=False)

    