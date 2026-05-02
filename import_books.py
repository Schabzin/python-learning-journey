import pandas as pd
import sqlite3
import os

def clear_db():
    conn = sqlite3.connect("books.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books")
    conn.commit()
    print("Database cleared")


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


def import_oxford():
    filepath = "price_lists/OUP Grade R-12 Price List 2025-26.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return[]
    
    df = pd.read_excel(filepath, header=7)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["ISBN"])

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

def import_marang():
    filepath = "price_lists/marang.xlsx"
    xl = pd.ExcelFile(filepath)
    print(f"\nMarang sheets: {xl.sheet_names}")
    df = pd.read_excel(filepath, sheet_name=0, header=None)
    for i, row in df.iterrows():
        print(f"Row {i}: {list(row)}")
        if i > 5:
            break
        return []
    
def check_all():
    files = {
        "HSE": "price_lists/HSE.xlsx",
        "Lectio": "price_lists/lectio.xlsx",
        "Lingua Franca": "price_lists/Lingua Franca Pricelist 2025-2026 - Posters prices to be updated.xlsx",
        "Macmillan": "price_lists/Macmillan_SA_Retail_Price_List_2025_2026_Final_.01.xlsx",
        "MML": "price_lists/MML Grades R - 12 Alphabetical Price List - 2024 - 2025 (3) (1).xlsx",
        "New Generation": "price_lists/new generation.xlsx",
        "Pelmo": "price_lists/Pelmo Book PublishersPrice List 2025.xlsx",
        "Vivlia": "price_lists/Pricelist 2025-2026 Vivlia Publishers final.xlsx",
        "Shooter": "price_lists/shooter.xlsx",
        "St Marys": "price_lists/st mary's.xlsx",
        "Answer Series": "price_lists/answer series.xlsx",
        "Trumpeter": "price_lists/trumpeter.xlsx",
    }
    
    for name, path in files.items():
        if not os.path.exists(path):
            print(f"\n{name}: FILE NOT FOUND")
            continue
        xl = pd.ExcelFile(path)
        print(f"\n{name} sheets: {xl.sheet_names}")
        df = pd.read_excel(path, sheet_name=0, header=None)
        for i, row in df.iterrows():
            print(f"  Row {i}: {list(row)}")
            if i > 4:
                break

check_all()
def import_shooter():
    filepath = "price_lists/shooter.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    df = pd.read_excel(filepath, sheet_name="caps")
    df.columns = df.columns.str.strip()
    all_data = []
    
    for _, row in df.iterrows():
        try:
            isbn = str(row.iloc[0]).strip()
            title = str(row.iloc[1]).strip()
            price_raw = str(row.iloc[3]).strip()
            
            digits_only = isbn.replace("-","").replace(" ","").replace(".","")
            if not digits_only.isdigit() or len(digits_only) < 10:
                continue
            
            try:
                price = float(price_raw.replace("R","").replace(",","."))
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
                "publisher": "Shooter"
            })
        except:
            continue
    
    print(f"Shooter: {len(all_data)} books found")
    return all_data

def import_stmarys():
    filepath = "price_lists/st mary's.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=1)
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip()
                title = str(row.iloc[1]).strip()
                grade = str(row.iloc[6]).strip() if len(row) > 6 else ""
                price_raw = str(row.iloc[4]).strip() if len(row) > 4 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",","."))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": "",
                    "language": "",
                    "price": price,
                    "book_type": "",
                    "publisher": "St Marys"
                })
            except:
                continue
    
    print(f"St Marys: {len(all_data)} books found")
    return all_data

def import_new_generation():
    filepath = "price_lists/new generation.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[1]).strip() if len(row) > 1 else ""
                title = str(row.iloc[2]).strip() if len(row) > 2 else ""
                grade = str(row.iloc[0]).strip() if len(row) > 0 else ""
                price_raw = str(row.iloc[6]).strip() if len(row) > 6 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(str(price_raw).replace("R","").replace(",","."))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": "",
                    "language": "",
                    "price": price,
                    "book_type": "",
                    "publisher": "New Generation"
                })
            except:
                continue
    
    print(f"New Generation: {len(all_data)} books found")
    return all_data

def import_hse():
    filepath = "price_lists/HSE.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                title = str(row.iloc[0]).strip() if len(row) > 0 else ""
                price_raw = str(row.iloc[2]).strip() if len(row) > 2 else "0"
                
                if title == "nan" or title == "" or len(title) < 5:
                    continue
                if any(x in title.upper() for x in ["PRICE", "VALID", "TEXTBOOK", "ORDER", "ACADEMIC"]):
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",","."))
                except:
                    price = 0.0
                
                if price == 0.0:
                    continue
                
                all_data.append({
                    "isbn": "",
                    "title": title,
                    "grade": "",
                    "subject": "",
                    "language": "",
                    "price": price,
                    "book_type": "",
                    "publisher": "HSE"
                })
            except:
                continue
    
    print(f"HSE: {len(all_data)} books found")
    return all_data

def import_lectio():
    filepath = "price_lists/lectio.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=2)
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[7]).strip() if len(row) > 7 else ""
                title = str(row.iloc[3]).strip() if len(row) > 3 else ""
                grade = str(row.iloc[4]).strip() if len(row) > 4 else ""
                language = str(row.iloc[2]).strip() if len(row) > 2 else ""
                book_type = str(row.iloc[5]).strip() if len(row) > 5 else ""
                price_raw = str(row.iloc[8]).strip() if len(row) > 8 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",","."))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": "",
                    "language": language,
                    "price": price,
                    "book_type": book_type,
                    "publisher": "Lectio"
                })
            except:
                continue
    
    print(f"Lectio: {len(all_data)} books found")
    return all_data

def import_lingua_franca():
    filepath = "price_lists/Lingua Franca Pricelist 2025-2026 - Posters prices to be updated.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip() if len(row) > 0 else ""
                title = str(row.iloc[1]).strip() if len(row) > 1 else ""
                grade = str(row.iloc[2]).strip() if len(row) > 2 else ""
                language = str(row.iloc[3]).strip() if len(row) > 3 else ""
                book_type = str(row.iloc[4]).strip() if len(row) > 4 else ""
                price_raw = str(row.iloc[5]).strip() if len(row) > 5 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",","."))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": "",
                    "language": language,
                    "price": price,
                    "book_type": book_type,
                    "publisher": "Lingua Franca"
                })
            except:
                continue
    
    print(f"Lingua Franca: {len(all_data)} books found")
    return all_data

def import_macmillan():
    filepath = "price_lists/Macmillan_SA_Retail_Price_List_2025_2026_Final_.01.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip() if len(row) > 0 else ""
                title = str(row.iloc[1]).strip() if len(row) > 1 else ""
                grade = str(row.iloc[3]).strip() if len(row) > 3 else ""
                subject = str(row.iloc[4]).strip() if len(row) > 4 else ""
                language = str(row.iloc[5]).strip() if len(row) > 5 else ""
                price_raw = str(row.iloc[2]).strip() if len(row) > 2 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",","."))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": subject,
                    "language": language,
                    "price": price,
                    "book_type": "",
                    "publisher": "Macmillan"
                })
            except:
                continue
    
    print(f"Macmillan: {len(all_data)} books found")
    return all_data

def import_pelmo():
    filepath = "price_lists/Pelmo Book PublishersPrice List 2025.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip() if len(row) > 0 else ""
                title = str(row.iloc[1]).strip() if len(row) > 1 else ""
                price_raw = str(row.iloc[3]).strip() if len(row) > 3 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",","."))
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
                    "publisher": "Pelmo"
                })
            except:
                continue
    
    print(f"Pelmo: {len(all_data)} books found")
    return all_data

def import_maskew():
    filepath = "price_lists/mml_price_list_2025-2026.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        
        header_row = None
        for i, row in df.iterrows():
            if str(row.iloc[0]).strip().upper() == "TITLE":
                header_row = i
                break
        
        if header_row is None:
            continue
        
        df = pd.read_excel(filepath, sheet_name=sheet, header=header_row)
        
        for _, row in df.iterrows():
            try:
                isbn_col2 = str(row.iloc[2]).strip() if len(row) > 2 else ""
                isbn_col1 = str(row.iloc[1]).strip() if len(row) > 1 else ""
                
                digits_col2 = isbn_col2.replace("-","").replace(" ","").replace(".","")
                digits_col1 = isbn_col1.replace("-","").replace(" ","").replace(".","")
                
                if digits_col2.isdigit() and len(digits_col2) >= 10:
                    isbn = isbn_col2
                    price_raw = str(row.iloc[4]).strip() if len(row) > 4 else "0"
                elif digits_col1.isdigit() and len(digits_col1) >= 10:
                    isbn = isbn_col1
                    price_raw = str(row.iloc[3]).strip() if len(row) > 3 else "0"
                else:
                    continue
                
                title = str(row.iloc[0]).strip()
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
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
                    "publisher": "Maskew Miller"
                })
            except:
                continue
    
    print(f"Maskew Miller: {len(all_data)} books found")
    return all_data

def import_vivlia():
    filepath = "price_lists/Pricelist 2025-2026 Vivlia Publishers final.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip() if len(row) > 0 else ""
                title = str(row.iloc[1]).strip() if len(row) > 1 else ""
                book_type = str(row.iloc[2]).strip() if len(row) > 2 else ""
                subject = str(row.iloc[3]).strip() if len(row) > 3 else ""
                price_raw = str(row.iloc[4]).strip() if len(row) > 4 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": "",
                    "subject": subject,
                    "language": "",
                    "price": price,
                    "book_type": book_type,
                    "publisher": "Vivlia"
                })
            except:
                continue
    
    print(f"Vivlia: {len(all_data)} books found")
    return all_data

def import_answer_series():
    filepath = "price_lists/answer series.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        current_subject = ""
        
        for _, row in df.iterrows():
            try:
                col0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                col1 = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
                col2 = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                col4 = str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else ""
                digits0 = col0.replace("-","").replace(" ","").replace(".","")
                if col0 and not digits0.isdigit() and col1 and "R" in col1:

                    title = col0
                    price_raw = col1.replace("R","").replace(",",".").strip()
                    
                    try:
                        price = float(price_raw)
                    except:
                        price = 0.0
                    
                    
                    digits2 = col2.replace("-","").replace(" ","").replace(".","")
                    if digits2.isdigit() and len(digits2) >= 10:
                        all_data.append({
                            "isbn": col2,
                            "title": title,
                            "grade": "",
                            "subject": "",
                            "language": "English",
                            "price": price,
                            "book_type": "",
                            "publisher": "Answer Series"
                        })
                    
                
                    digits4 = col4.replace("-","").replace(" ","").replace(".","")
                    if digits4.isdigit() and len(digits4) >= 10:
                        all_data.append({
                            "isbn": col4,
                            "title": title,
                            "grade": "",
                            "subject": "",
                            "language": "Afrikaans",
                            "price": price,
                            "book_type": "",
                            "publisher": "Answer Series"
                        })
            except:
                continue
    
    print(f"Answer Series: {len(all_data)} books found")
    return all_data

def import_trumpeter():
    filepath = "price_lists/trumpeter.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=1)
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip()
                title = str(row.iloc[1]).strip()
                grade = str(row.iloc[4]).strip() if len(row) > 4 else ""
                price_raw = str(row.iloc[5]).strip() if len(row) > 5 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": "",
                    "language": "",
                    "price": price,
                    "book_type": "",
                    "publisher": "Trumpeter"
                })
            except:
                continue
    
    print(f"Trumpeter: {len(all_data)} books found")
    return all_data

def import_brainit():
    filepath = "price_lists/BrainbIT Theory and Dandel10n Delphi Books 2026.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    df = pd.read_excel(filepath, sheet_name="Table 5", header=0)
    all_data = []
    
    for _, row in df.iterrows():
        try:
            title = str(row.iloc[0]).strip()
            grade = str(row.iloc[1]).strip()
            price_raw = str(row.iloc[2]).strip()
            
            if title == "nan" or title == "" or title == "Title":
                continue
            
            try:
                price = float(price_raw.replace("R","").replace(",",".").strip())
            except:
                price = 0.0
            
            all_data.append({
                "isbn": "",
                "title": title,
                "grade": grade,
                "subject": "",
                "language": "",
                "price": price,
                "book_type": "",
                "publisher": "BrainIT"
            })
        except:
            continue
    
    print(f"BrainIT: {len(all_data)} books found")
    return all_data

def import_mind_action():
    filepath = "price_lists/MIND ACTION SERIES - PerSubject.PRINT & E-BOOK RETAIL PRICE LIST.2026.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=3)
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[6]).strip()
                title = str(row.iloc[2]).strip()
                grade = str(row.iloc[3]).strip()
                price_raw = str(row.iloc[8]).strip()
                book_type = str(row.iloc[4]).strip()
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
                except:
                    price = 0.0
                
                all_data.append({
                    "isbn": isbn,
                    "title": title,
                    "grade": grade,
                    "subject": sheet,
                    "language": "",
                    "price": price,
                    "book_type": book_type,
                    "publisher": "Mind Action"
                })
            except:
                continue
    
    print(f"Mind Action: {len(all_data)} books found")
    return all_data

def import_nb_publishers():
    filepath = "price_lists/NB PUBLISHERS PRICE LIST - PRYSLYS 1 April 2025.xls"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath, engine="xlrd")
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None, engine="xlrd")
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip()
                title = str(row.iloc[1]).strip()
                price_raw = str(row.iloc[2]).strip() if len(row) > 2 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
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
                    "publisher": "NB Publishers"
                })
            except:
                continue
    
    print(f"NB Publishers: {len(all_data)} books found")
    return all_data

def import_pharos():
    filepath = "price_lists/PHAROS PRICE LIST - PRYSLYS 1 APRIL 2025.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip()
                title = str(row.iloc[1]).strip() if len(row) > 1 else ""
                price_raw = str(row.iloc[2]).strip() if len(row) > 2 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
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
                    "publisher": "Pharos"
                })
            except:
                continue
    
    print(f"Pharos: {len(all_data)} books found")
    return all_data

def import_best_books():
    filepath = "price_lists/Best Books Price List 2025-2026.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    xl = pd.ExcelFile(filepath)
    all_data = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        for _, row in df.iterrows():
            try:
                isbn = str(row.iloc[0]).strip()
                title = str(row.iloc[1]).strip() if len(row) > 1 else ""
                price_raw = str(row.iloc[2]).strip() if len(row) > 2 else "0"
                
                digits_only = isbn.replace("-","").replace(" ","").replace(".","")
                if not digits_only.isdigit() or len(digits_only) < 10:
                    continue
                
                try:
                    price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
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
                    "publisher": "Best Books"
                })
            except:
                continue
    
    print(f"Best Books: {len(all_data)} books found")
    return all_data

def import_lux():
    filepath = "price_lists/LUX VERBI PRICE LIST - PRYSLYS 1 APRIL 2025.xlsx"
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    
    df = pd.read_excel(filepath, sheet_name=0, header=11)
    df.columns = df.columns.str.strip()
    all_data = []
    
    for _, row in df.iterrows():
        try:
            isbn = str(row.iloc[0]).strip()
            title = str(row.iloc[1]).strip()
            price_raw = str(row.iloc[3]).strip()
            
            digits_only = isbn.replace("-","").replace(" ","").replace(".","")
            if not digits_only.isdigit() or len(digits_only) < 10:
                continue
            
            try:
                price = float(price_raw.replace("R","").replace(",",".").replace(" ",""))
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
                "publisher": "LUX"
            })
        except:
            continue
    
    print(f"LUX: {len(all_data)} books found")
    return all_data

def diagnose(name, filepath):
    if not os.path.exists(filepath):
        print(f"\n{name}: FILE NOT FOUND")
        return
    xl = pd.ExcelFile(filepath)
    print(f"\n{name} sheets: {xl.sheet_names}")
    df = pd.read_excel(filepath, sheet_name=0, header=None)
    for i, row in df.iterrows():
        print(f"Row {i}: {list(row)}")
        if i > 6:
            break


clear_db()

data = import_pulse()
if data:
    save_to_db(data)

data = import_oxford()
if data:
    save_to_db(data)

data = import_marang()

data = import_shooter()
if data: save_to_db(data)

data = import_stmarys()
if data: save_to_db(data)

data = import_new_generation()
if data: save_to_db(data)

data = import_hse()
if data: save_to_db(data)

data = import_lectio()
if data: save_to_db(data)

data = import_lingua_franca()
if data: save_to_db(data)

data = import_macmillan()
if data: save_to_db(data)

data = import_pelmo()
if data: save_to_db(data)

data = import_maskew()
if data: save_to_db(data)

data = import_vivlia()
if data: save_to_db(data)

data = import_answer_series()
if data: save_to_db(data)

data = import_trumpeter()
if data: save_to_db(data)

data = import_brainit()
if data: save_to_db(data)

data = import_mind_action()
if data: save_to_db(data)

data = import_nb_publishers()
if data: save_to_db(data)

data = import_pharos()
if data: save_to_db(data)

data = import_best_books()
if data: save_to_db(data)

data = import_lux()
if data: save_to_db(data)

