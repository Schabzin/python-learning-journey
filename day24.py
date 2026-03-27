import sqlite3
import pandas as pd

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()

print(df.columns.tolist())

print(f"Total clients: {len(df)}")
print(f"Total revenue: R{df['amount'].sum()}")
print(f"Average invoice: R{df['amount'].mean():.2f}")
print(f"Paid clients: {len(df[df['status'] == 'Paid'])}")
print(f"Pendind clients: {len(df[df['status'] == 'Pending'])}")

df["VAT"] = df["amount"] * 0.15
df["Total"] = df["amount"] + df["VAT"]
print(df)
print(df["status"].tolist())
print(df["amount"].max())
print(df.sort_values("amount", ascending=False).head(3))

df_unpaid = df[df["status"] == "Unpaid"]
print(df_unpaid)
print(f"Total outstanding debt: R{df_unpaid['amount'].sum():.2f}")

df.to_csv("kalikeng_business_report.csv", index=False)
print("Report saved!")
