import sqlite3
import pandas as pd

conn = sqlite3.connect("books.db")
df = pd.read_sql_query("SELECT isbn, title,grade , subject, language, price, publisher FROM books", conn)
conn.close()

df["isbn"] = df["isbn"].astype(str).str.replace(".0", "", regex=False)
df.to_excel("master_price_list.xlsx", index=False, sheet_name="MASTER")
print(f"Exported {len(df)} books to master_price_list.xlsx")