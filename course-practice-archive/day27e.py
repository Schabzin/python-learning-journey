import sqlite3
import pandas as pd
import re

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()

df["phone_valid"] = df["phone"].str.match(r"^0\d{9}$")
df["clean_price"] = df["amount"].astype(str).str.replace(r"[^\d.]","", regex=True)
df["extracted"] = df["phone"].str.extract(r"^(\d{3})")
df["priority"] = df.apply(
    lambda row: "High Priority" if row["status"] == "Unpaid" and row["amount"] > 3000 else "Normal", axis=1
)
print(df)
df.to_csv("kalikeng_regex_report.csv", index=False)
print("Report saved!")