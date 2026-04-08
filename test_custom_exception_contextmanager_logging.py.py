import logging
import sqlite3
import pandas as pd

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test.log"),
        logging.StreamHandler()
    ]
)

class InvalidPriceError(Exception):
    pass

def add_product(name, amount):
    if amount <= 0:
     raise InvalidPriceError(f"Amount cannot be negetive: {amount}")

class InvalidStockError(Exception):
    pass

def validate_stock(stock):
    if stock < 0:
        raise InvalidStockError(f"Invalid stock: {stock}")
    return True

try:
    conn = sqlite3.connect("test.db")
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    logging.info(f"Successfuly loaded {len(df)} products")
    print(df)
    for _, row in df.iterrows():
        if row["stock"] < 60:
            logging.warning(f"Low stock: {row['name']} - {row['stock']}")
except Exception as e:
    logging.error(f"Failed to load products: {e}")