import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()

plt.figure(figsize=(10, 6))

plt.bar(df["name"], df["amount"], color="steelblue")
plt.title("Client Amounts")
plt.xlabel("Amount (R)")
plt.ylabel("Client")
plt.savefig("kalikeng_bar_chart.png")
plt.show()
plt.clf()

plt.barh(df["name"], df["amount"], color="steelblue")
plt.title("Client Amounts")
plt.xlabel("Amount (R)")
plt.ylabel("Client")
plt.savefig("kalikeng_barh_chart.png")
plt.show()
plt.clf()

plt.plot(df["name"], df["amount"], marker="o", color="navy")
plt.title("Client Amount Trend")
plt.xlabel("Client")
plt.ylabel("Amount (R)")
plt.show()
plt.clf()

colors = ["#1B3A5C", "#C85A00"]
paid = len(df[df["status"] == "Paid"])
unpaid = len(df[df["status"] == "Unpaid"])
plt.pie([paid, unpaid], labels=["Paid", "Unpaid"], colors=colors, autopct="%1.1f%%")
plt.title("Payment Status")
plt.savefig("kalikeng_pie_chart.png")
plt.show()
plt.clf()

print("All charts saved!")    

