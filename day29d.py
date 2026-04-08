import json
import os
import pandas as pd
import logging

folder = "kalikeng_file_manager"
all_data = []
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("kalikeng.log"),
        logging.StreamHandler()
    ]
)
os.makedirs("kalikeng_file_manager", exist_ok=True)

clients_january = pd.DataFrame([
    {"name": "Sechaba", "phone": "0732239762", "amount": 5000, "status": "Unpaid"},
    {"name": "Nomvula", "phone": "0611813424", "amount": 3200, "status": "Paid"},
    {"name": "Rorisang", "phone": "0635922914", "amount": 4500, "status": "Unpaid"}
])
with open(os.path.join("kalikeng_file_manager", "january.json"), "w") as f:
    json.dump(clients_january. to_dict(orient="records"), f, indent=4)

clients_february = pd.DataFrame([
    {"name": "Sechaba", "phone": "0732239762", "amount": 6000, "status": "Paid"},
    {"name": "Nomvula", "phone": "0611813424", "amount": 2800, "status": "Unpaid"},
    {"name": "Rorisang", "phone": "0635922914", "amount":3900, "status": "Paid" }
])
with open(os.path.join("kalikeng_file_manager", "february.json"), "w") as f:
    json.dump(clients_february. to_dict(orient="records"), f, indent=4)

clients_march = pd.DataFrame([
    {"name": "Sechaba", "phone": "0732239762", "amount": 4500, "status": "Unpaid"},
    {"name": "Nomvula", "phone": "0611813424", "amount": 5700, "status": "Paid"},
    {"name": "Rorisang", "phone": "063592294", "amount": 2200, "status": "Unpaid"}
])
with open(os.path.join("kalikeng_file_manager", "march.json"), "w") as f:
    json.dump(clients_march. to_dict(orient="records"), f, indent=4)

for filename in os.listdir(folder):
    if filename.endswith(".json"):
        filepath = os.path.join(folder, filename)
        df = pd.read_json(filepath)
        all_data.append(df)

combined = pd.concat(all_data, ignore_index=True)
print(combined)
df.to_csv("kalikeng_annual_report.csv", index=False)

logging.info(f"Successfuly loaded {len(df)} records")
print("File management complete!")