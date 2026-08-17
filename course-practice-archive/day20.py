import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://books.toscrape.com"
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")

books = soup.find_all("article", class_="product_pod")

book_list = []
for book in books[:10]:
    title = book.find("h3").find("a")["title"].strip()
    price = book.find("p", class_="price_color").text.strip()
    book_list.append({"Title": title, "Price": price})

df = pd.DataFrame(book_list)

df["Price"] = df["Price"].str.encode('ascii', 'ignore').str.decode('ascii').str.replace("£", "").str.strip().astype(float)

pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print("\n--- All 10 Books ---")
print(df.to_string(index=False))

print("\n--- Books Under £20 ---")
small = df[df["Price"] < 20]
print(small.to_string(index=False))

pd.set_option('display.max_colwidth', None)
pd.set_option('display.width',None)


    
    