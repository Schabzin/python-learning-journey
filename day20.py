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
print(df)


df["Price"] = df["Price"].str.encode('ascii', 'ignore').str.decode('ascii').str.replace("£", "").astype(float)

small = df[df["Price"] < 20]
print(small)

df.to_csv("books_scraped.csv", index=False)



