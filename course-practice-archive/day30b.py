import logging
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("kaliekng_sytem.log"),
        logging.StreamHandler()
    ]
)

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()
logging.info(f"Successfully loaded {len(df)} clients")

print(f"Total clients: {len(df)}")
print(f"Total revenue: R{df['amount'].sum():.2f}")
print(f"Average invoice: R{df['amount'].mean():.2f}")
print(f"Highest invoice: R{df['amount'].max():.2f}")
print(f"Paid clients: {len(df[df['status'] == 'Paid'])}")
print(f"Unpaid clients: {len(df[df['status'] == 'Unpaid'])}")

df["VAT"] = df["amount"] * 0.15
df["Total"] = df["amount"] + df["VAT"]

plt.figure(figsize=(14,6))

plt.subplot(2,2,1)
plt.bar(df["name"], df["amount"], color= "steelblue")
plt.title("Client Amounts")
plt.xlabel("Amount (R)")
plt.ylabel("Client")

plt.subplot(2,2,2)
plt.barh(df["name"], df["amount"], color= "steelblue")
plt.title("Client Amounts")
plt.xlabel("Amount (R)")
plt.ylabel("Clients")

plt.subplot(2,2,3)
plt.plot(df["name"], df["amount"], marker="o", color="navy")
plt.title("Clients Amount Trend")
plt.xlabel("Client")
plt.ylabel("Amount (R)")

plt.subplot(2,2,4)
colors =["#1B3A5C", "#C85A00"]
paid = len(df[df["status"] == "Paid"])
unpaid = len(df[df["status"] == "Unpaid"])
plt.pie([paid,unpaid], labels=["Paid", "Unpaid"], colors=colors, autopct="%1.1f%%")
plt.title("Payment Status")
plt.tight_layout()
plt.savefig("kalikeng_dashboard.png")
plt.show()

df.to_csv("kalikeng_report.csv", index=False)
logging.info(f"Report and Dashboard saved")

print("Report generated!")