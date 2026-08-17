import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()

plt.bar(df["name"], df["amount"])
plt.title("kalikeng Client Amounts")
plt.xlabel("Client")
plt.ylabel("Amount (R)")
plt.savefig("kalikeng_bar_chart.png")
plt.show()

paid = len(df[df["status"] == "Paid"])
unpaid = len(df["status"] == "Unpaid")
plt.pie([paid, unpaid], labels=["Paid", "Unpaid"], autopct="%1.1f%%")
plt.title("Payment Status")
plt.savefig("kalikeng_pie_chart.png")
plt.show()

print("Charts saved")
 