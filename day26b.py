import requests
from bs4 import BeautifulSoup
import pandas as pd

all_books = []
for page in range(1, 6): # start with 5 pages first
    url = f"https://books.toscrape.com/catalogue/page-{page}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")
    books = soup.find_all("article", class_="product_pod")
    for book in books:
        title = book.find("h3").find("a")["title"]
        price = book.find("p", class_="price_color").text
        all_books.append({"title": title, "price": price})

df = pd.DataFrame(all_books)
print(df)
df.to_csv("books_scraped.csv", index=False)
print(f"Total books scraped: {len(df)}")