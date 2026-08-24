import pandas as pd
import sqlite3

def create_books_db():
    conn = sqlite3.connect("textbooks.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            publisher TEXT NOT NULL,
            grade TEXT,
            book_type TEXT,
            price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("textbooks.db created")

def import_publisher_pricelist(excel_path, publisher_name):
    df = pd.read_excel(excel_path, header=11)
    df = df.dropna(subset=["ISBN", "TITLE"])
    conn = sqlite3.connect("textbooks.db")
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO books (title, publisher, grade, book_type, price)
            VALUES (?, ?, ?, ?, ?)
        """, (row["TITLE"], publisher_name, "", "", row["RRP Price \n1 July 2026 - \n30 June 2027"]))
    conn.commit()
    conn.close()
    print(f"Imported {len(df)} books from {publisher_name}")

create_books_db()

conn = sqlite3.connect("textbooks.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
conn.close()

import_publisher_pricelist(
    "C:/Users/Sechaba/Documents/business/price list 2026-2027/maskewmillerlearningupdatedpricelists20262027/20262027_Grades_0407_Price_list_MML_Hei.xlsx",
    "Maskew Miller Longman"
)

