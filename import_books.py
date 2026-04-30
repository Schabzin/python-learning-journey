import pandas as pd
import sqlite3
import os

def import_pulse():
    filepath = "price_lists/PULSE.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    xl = pd.ExcelFile(filepath)
    all_data = []

    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            isbn = str(row[0]).strip()
            title = str(row[1]).strip() if len(row) > 1 else ""
            price_raw = str([2]).strip() if len(row) > 2 else "0"

            if not isbn.replace("_", "").isdigit():
                continue

            price_clean = price_raw.replace("R", "").replace("_", ".").strip()
            try:
                price = float(price_clean)
            except:
                price = 0.0

            all_data.append({
                "isbn": isbn,
                "title": title,
                "grade": "",
                "subject": "",
                "language": "",
                "price": price,
                "book_type": "",
                "publisher": "Pulse"
            })
        
    print(f"Pulse: {len(all_data)} books found")
    return all_data

def save_to_db(data):
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO books (isbn, title, grade, subject,language, price, book_type, publisher)
        VALUES (:isbn, :title, :grade, :subject, :language, :price, :book_type, :publisher)
    """, data)
    conn.commit()
    conn.close()
    print(f"Saved {len(data)} books to database")

data = import_pulse()
if data:
    save_to_db(data)

def import_oxford():
    filepath = "price_lists/OUP Grade R-12 Price List 2025-26.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return[]
    
    df = pd.read_excel(filepath, header=7)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["ISBN"])
    print(f"Oxford rows after dropna: {len(df)}")
    print(df["ISBN"].head(10))

    all_data = []
    
    for _, row in df.iterrows():
            isbn = str(row["ISBN"]).strip()
            digits_only = isbn.replace("-", "").replace(" ", "").replace(".", "")
        
            if isbn == "nan" or isbn == "" or not digits_only.isdigit() or len(digits_only) < 10:
                continue

            all_data.append({
                "isbn":isbn,
                "title": str(row["TITLE"]).strip() if pd.notna(row["TITLE"]) else "",
                "grade": str(row["GRADE"]).strip() if pd.notna(row["GRADE"]) else "",
                "subject": str(row["SUBJECT"]).strip() if pd.notna(row["SUBJECT"]) else "",
                "language": str(row["LANGUAGE"]).strip() if pd.notna(row["LANGUAGE"]) else "",
                "price": float(row["PRICE"]) if pd.notna(row["PRICE"]) else 0.0,
                "book_type": str(row["TYPE"]).strip() if pd.notna(row["TYPE"]) else "",
                "publisher": "OXFORD"
            })
    print(f"Oxford: {len(all_data)} books found")
    return all_data

data = import_pulse()
if data:
    save_to_db(data)

data = import_oxford()
if data:
    save_to_db(data)