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

def add_isbn_column():
    conn = sqlite3.connect("textbooks.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE books ADD COLUMN isbn TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        print("Column already exists")
    conn.close()

def import_publisher_pricelist(excel_path, publisher_name, header_row, isbn_col, title_col, price_col, grade_col=None):
    df = pd.read_excel(excel_path, header=header_row)
    df.columns = df.columns.str.strip()
    print(repr(df.columns.tolist()))
    df = df.dropna(subset=[isbn_col, title_col])
    conn = sqlite3.connect("textbooks.db")
    cursor = conn.cursor()
    for _, row in df.iterrows():
        grade_value = str(row[grade_col]) if grade_col else ""
        cursor.execute("""
            INSERT INTO books (title, publisher, grade, book_type, price, isbn)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (row[title_col], publisher_name, grade_value, "", row[price_col], str(row[isbn_col])))
    conn.commit()
    conn.close()
    print(f"Imported {len(df)} books from {publisher_name}")

create_books_db()
add_isbn_column()

conn = sqlite3.connect("textbooks.db")
cursor = conn.cursor()
cursor.execute("DELETE FROM books")
conn.commit()
conn.close()

import_publisher_pricelist(
    "C:/Users/Sechaba/Documents/business/price list 2026-2027/maskewmillerlearningupdatedpricelists20262027/20262027_Grades_0407_Price_list_MML_Hei.xlsx", "Maskew Miller Longman", 11, "ISBN", "TITLE",
    "RRP Price \n1 July 2026 - \n30 June 2027"
    
)

import_publisher_pricelist(
    "C:/Users/Sechaba/Documents/business/price list 2026-2027/oxforduniversitypresspricelistseffective1july20263/OUP_Grade_R12_Price_List_202627.xlsx", "Oxford Successful", 6,
    "ISBN", "TITLE", "PRICE", "GRADE"
)


  
