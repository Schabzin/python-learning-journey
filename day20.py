import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://books.toscrape.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

books = soup.find_all("article", class_="product_pod")

book_list = []
for book in books[:10]:
    title = book.find("h3").find("a")["title"]
    price = book.find("p", class_="price_color").text
    book_list.append({"Title": title, "Price": price})
 

df = pd.DataFrame(book_list)

df["Price"] = df["Price"].str.encode('ascii', 'ignore').str.decode('ascii').str.replace("£", "").str.strip().astype(float)

print("\n--- All 10 Books ---")
print(df.to_string(index=False))

print("\n--- Books Under £20 ---")
small = df[df["Price"] < 20]
print(small.to_string(index=False))

df.to_csv("books_scraped.csv", index=False)

