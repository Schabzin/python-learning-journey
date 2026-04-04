import logging
import sqlite3
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("kalikeng.log"),
        logging.StreamHandler()
    ]
)

try:
    conn = sqlite3.connect("kalikeng.db")
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    logging.info(f"Successfully loaded {len(df)} clients")
    print(df)
    for _, row in df.iterrows():
        if row["status"] == "Unpaid" and row["amount"] > 4000:
            logging.warning(f"High value unpaid: {row['name']} - R{row['amount']}")
            df.to_csv("kalikeng_log_report.csv", index=False)
except Exception as e:
    logging.error(f"Failed to load clients: {e}")
    print("Error occured - check kalikeng.log")
                  