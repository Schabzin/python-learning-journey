import logging
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import re
import os
import json

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
folder = "kalikeng_final"

class InvalidAmountError(Exception):
    pass

class InvalidPhoneError(Exception):
    pass
 
class InvalidStatusError(Exception):
    pass

def validate_phone(phone):
    pattern = r"^0\d{9}$"
    if not re.match(pattern, phone):
        raise InvalidPhoneError(f"Invalid phone number: {phone}")
    return True

def validate_status(status):
    if status not in ["Paid", "Unpaid"]:
        raise InvalidStatusError(f"Invalid status: {status}")
    return True

def validate_client(name, phone, amount, status):
    if amount < 0:
        raise InvalidAmountError(f"Amount cannot be negative: {amount}")
    validate_phone(phone)
    validate_status(status)
                                
for _, row in df.iterrows():
    try:
        validate_client(row["name"], row["phone"], row["amount"], row["status"])
        logging.info(f"Valid client: {row['name']}")
    except (InvalidAmountError, InvalidPhoneError, InvalidStatusError) as e:
        logging.warning(f"Invalid client{row['name']}: {e}")


print(f"Total clients: {len(df)}")
print(f"Total revenue: R{df['amount'].sum():.2f}")
print(f"Average invoice: R{df['amount'].mean():.2f}")
print(f"Highest invoice: R{df['amount'].max():.2f}")
print(f"Paid clients: {len(df[df['status'] == 'Paid'])}")
print(f"Unpaid clients: {len(df[df['status'] == 'Unpaid'])}")

df["VAT"] =df["amount"] * 0.15
df["Total"] =df["amount"] + df["VAT"]

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

paid_df = df[df["status"]== "Paid"]
unpaid_df = df[df["status"] == "Unpaid"]
os.makedirs("kalikeng_final", exist_ok=True)

with open(os.path.join("kalikeng_final", "paid_clients.json"), "w") as f:
    json.dump(paid_df.to_dict(orient="records"), f, indent=4)

with open(os.path.join("kalikeng_final", "unpaid_client.json"), "w") as f:
    json.dump(unpaid_df.to_dict(orient="records"), f, indent=4)

df.to_csv("kalikeng_final_report.csv", index=False)
logging.info("Paid and Unpaid JSON files saved")
print("Kalikeng Automation System Complete!")

