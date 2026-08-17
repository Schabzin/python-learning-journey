import sqlite3
import pandas as pd

with sqlite3.connect("kalikeng.db") as conn:
    df = pd.read_sql_query("SELECT * FROM clients", conn)

class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        print("Connection opened")
        return self.conn
    
    def __exit__(self, exc_type,exc_val, exc_tb):
        self.conn.close()
        print("Connection closed")

try:
    with DatabaseConnection("kalikeng.db") as conn:
        df = pd.read_sql_query("SELECT * FROM clients", conn)
        print(df)
        df.to_csv("kalikeng_context.csv", index=False)
except Exception as e:
    print(f"Database error: {e}")


