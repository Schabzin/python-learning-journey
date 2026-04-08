import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("test.db")
df = pd.read_sql_query("SELECT * FROM products", conn)
conn.close()

plt.bar(df["name"], df["price"], color="steelblue")
plt.title("Product Price")
plt.xlabel("Price (R)")
plt.ylabel("Product")
plt.savefig("test_bar_chart.png")
plt.show()
plt.clf()

df["value"] = df["price"] * df["stock"]

plt.pie(df["value"], labels=df["name"], autopct="%1.1f%%")
plt.title("Product Value Share")
plt.savefig("test_pie_chart.png")
plt.show()
plt.clf()
print("Charts saved!")
