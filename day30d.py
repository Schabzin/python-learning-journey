import logging
import json
import os
import pandas as pd
import sqlite3

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

paid_df = df[df["status"] == "Paid"]
unpaid_df = df[df["status"] == "Unpaid"]

os.makedirs("kalikeng_organised", exist_ok=True)
with open(os.path.join("kalikeng_organised", "paid_clients.json"), "w") as f:
    json.dump(paid_df.to_dict(orient="records"), f, indent=4)

with open(os.path.join("kalikeng_organised", "unpaid_clients.json"), "w") as f:
    json.dump(unpaid_df.to_dict(orient="records"), f, indent=4)

all_data = []
for filename in os.listdir("kalikeng_organised"):
    if filename.endswith(".json"):
        filepath = os.path.join("kalikeng_organised", filename)
        df = pd.read_json(filepath)
        logging.info(f"Loaded {filename} - {len(df)} records")
        df["file_source"] = filename.replace(".json", "")
        all_data.append(df)

combined = pd.concat(all_data, ignore_index=True)
combined.to_csv("kalikeng_organised.csv", index=False)
print("File organiser complete!")