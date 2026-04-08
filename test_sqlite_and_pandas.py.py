import sqlite3
import pandas as pd

conn = sqlite3.connect("test.db")
df = pd.read_sql_query("SELECT * FROM products", conn)
conn.close()

print(f"Total products:{len(df)}")
print(f"Expensive product: R{df['price'].max():.2f}")
df["value"] = df["price"] * df["stock"]
print(df.sort_values("value", ascending=False).head(3))
df.to_csv("products_report.csv", index=False)