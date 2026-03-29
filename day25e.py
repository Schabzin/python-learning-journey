import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn=sqlite3.connect("kalikeng.db")
df=pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()

plt.figure(figsize=(18,10))

plt.suptitle("Kalikeng Trading - Client Dashboard", fontsize=16, fontweight="bold")
plt.subplot(2,3,1)
plt.bar(df["name"], df["amount"], color="steelblue")
plt.title("Client Amounts")
plt.xlabel("Amount (R)")
plt.ylabel("Client")

plt.subplot(2,3,2)
plt.barh(df["name"], df["amount"], color="steelblue")
plt.title("Client Amounts")
plt.xlabel("Amoint (R)")
plt.ylabel("Client")

plt.subplot(2,3,3)
plt.plot(df["name"], df["amount"], marker="o", color="navy")
plt.title("Client Amount Trend")
plt.xlabel("Client")
plt.ylabel("Amount (R)")

plt.subplot(2,3,4)
colors= ["#1B3A5C", "#C85A00"]
paid= len(df[df["status"] == "Paid"])
unpaid= len(df[df["status"] == "Unpaid"])
plt.pie([paid, unpaid], labels= ["Paid", "Unpaid"], colors= colors, autopct= "%1.1f%%")

sns.set_theme(style= "whitegrid")

plt.subplot(2,3,5)
sns.barplot(x= "name", y= "amount", data= df, palette= "Blues_d")
plt.title("Client Amounts")
plt.xlabel("Client")
plt.ylabel("Amount (R)")
plt.annotate("Highest client", xy=(0, 7500), xytext= (1, 7000),
             arrowprops=dict(arrowstyle= "-"), fontsize=9)

plt.subplot(2,3,6)
sns.boxplot(x= "status", y= "amount", data= df, palette= "Set2")
plt.title("Amount Distribution by status")
plt.tight_layout()
plt.savefig("kalikeng_chart.png")
plt.show()