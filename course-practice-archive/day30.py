import logging
import sqlite3
import pandas as pd
import re

logging.basicConfig(
    level= logging.DEBUG,
    format= "%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("kalikeng_system.log"),
        logging.StreamHandler()
    ]
)

class InvalidAmountError (Exception):
    pass
def validate_client(name, phone, amount,status):
    if amount < 0:
        raise InvalidAmountError(f"Amount cannoot be negative: {amount}")
    validate_phone(phone)
    validate_status(status)

class InvalidPhoneError (Exception):
    pass
def validate_phone(phone):
    pattern = r"^0\d{9}$"
    if not re.match(pattern, phone):
        raise InvalidPhoneError(f"Invalid phone number: {phone}")
    return True

class InvalidStatusError (Exception):
    pass
def validate_status(status):
    if status not in ["Paid", "Unpaid"]:
        raise InvalidStatusError(f"Invalid status: {status}")
    return True

with sqlite3.connect("kalikeng.db") as conn:
    df = pd.read_sql_query("SELECT * FROM clients", conn)

    valid_clients = []
    for _, row in df.iterrows():
        try:
            validate_client(row["name"], row["phone"], row["amount"], row["status"])
            logging.info(f"Valid client: {row['name']}")
            valid_clients.append(row)
        except (InvalidAmountError, InvalidPhoneError, InvalidStatusError) as e:
            logging.warning(f"Invalid client {row['name']}: {e}")
   