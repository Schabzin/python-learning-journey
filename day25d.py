import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect("kalikeng.db")
df = pd.read_sql_query("SELECT * FROM clients", conn)
conn.close()

sns.set_theme(style="whitegrid")

sns.barplot(x="name", y="amount", data=df, palette="Blues_d")
plt.title("Client Amounts")
plt.xlabel("Client")
plt.ylabel("Amount (R)")
plt.annotate("Highest client", xy=(0, 7500), xytext=(1, 7000),
             arrowprops=dict(arrowstyle="-"), fontsize=9)
plt.savefig("kalikeng_bar_chart.png")
plt.show()

sns.boxplot(x="status", y="amount", data=df, palette="Set2")
plt.title("Amount Distribution by status")
plt.savefig("kalikeng_box_chart.png")
plt.show()

print("Done!")