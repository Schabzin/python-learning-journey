import os
import pandas as pd

folder = "monthly_reports"
all_data = []

os.makedirs("monthly_reports", exist_ok=True)

january = pd.DataFrame([
    {"name": "Sechaba", "amount": 5000, "status": "Unpaid"},
    {"name": "Nomvula", "amount": 3200, "status": "Paid"},
    {"name": "Rorisang", "amount": 4500, "status": "Unpaid"}
])
january.to_csv("monthly_reports/january.csv", index=False)

february = pd.DataFrame([
    {"name": "Sechaba", "amount": 6000, "status": "Paid"},
    {"name": "Nomvula", "amount": 2800, "status": "Unpaid"},
    {"name": "Rorisang", "amount": 3900, "status": "Paid"}
])
february.to_csv("monthly_reports/february.csv", index=False)

march = pd.DataFrame([
    {"name": "Sechaba", "amount": 4500, "status": "Unpaid"},
    {"name": "Nomvula", "amount": 5100, "status": "Paid"},
    {"name": "Rorisang", "amount": 2200, "status": "Unpaid"}
])
march.to_csv("monthly_reports/march.csv", index=False)

for filename in os.listdir(folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(folder, filename)
        df = pd.read_csv(filepath)
        all_data.append(df)

combined = pd.concat(all_data, ignore_index=True)
print(combined)
df.to_csv("kalikeng_quarterly_report.csv", index=False)
print("Quarterly report saved!")