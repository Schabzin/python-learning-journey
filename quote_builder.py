import sqlite3
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import date

# ── COLOURS ───────────────────────────────────────────────────────────────────
BLACK   = "1A1A1A"
ORANGE  = "C85A00"
WHITE   = "FFFFFF"
LGREY   = "F5F5F5"
LORANGE = "FFF3E0"
MGREY   = "CCCCCC"

def fill(hex_color):
    return PatternFill("solid", start_color=hex_color, fgColor=hex_color)

def font(bold=False, color=BLACK, size=10):
    return Font(name="Arial", bold=bold, color=color, size=size)

def border():
    s = Side(style="thin", color=MGREY)
    return Border(left=s, right=s, top=s, bottom=s)

def search_books(query):
    conn = sqlite3.connect("books.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Search by ISBN or title
    cursor.execute("""
        SELECT isbn, title, grade, language, price, publisher 
        FROM books 
        WHERE isbn LIKE ? OR title LIKE ?
        LIMIT 20
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def build_quote(items, school, ref_no):
    wb = Workbook()
    ws = wb.active
    ws.title = "QUOTATION"

    # Column widths
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["C"].width = 8
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 14
    ws.column_dimensions["G"].width = 16

    # ── HEADER ────────────────────────────────────────────────────────────────
    ws.merge_cells("A1:G1")
    ws["A1"] = "KALIKENG TRADING AND PROJECTS CC"
    ws["A1"].font = font(bold=True, size=16, color=WHITE)
    ws["A1"].fill = fill(BLACK)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:G2")
    ws["A2"] = "Reg No: 2010/007041/23  |  VAT No: 4340257320  |  Tel: 073 223 9762  |  kalikengtrading@gmail.com"
    ws["A2"].font = font(size=9, color=ORANGE)
    ws["A2"].fill = fill(BLACK)
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A3:G3")
    ws["A3"] = "B-BBEE LEVEL 1  |  100% BLACK OWNED  |  135% PROCUREMENT RECOGNITION"
    ws["A3"].font = font(bold=True, size=9, color=WHITE)
    ws["A3"].fill = fill(BLACK)
    ws["A3"].alignment = Alignment(horizontal="center")

    # Orange line
    for col in range(1, 8):
        ws.cell(row=4, column=col).fill = fill(ORANGE)
    ws.row_dimensions[4].height = 4

    # ── QUOTE DETAILS ─────────────────────────────────────────────────────────
    ws.row_dimensions[5].height = 6
    details = [
        (6, "QUOTATION NO:", ref_no, "DATE:", str(date.today().strftime("%d %B %Y"))),
        (7, "SCHOOL / CLIENT:", school, "PREPARED BY:", "Sechaba Mofokeng"),
    ]
    for row, l1, v1, l2, v2 in details:
        ws.row_dimensions[row].height = 18
        for col, val, bold, bg in [
            ("A", l1, True, LGREY), ("B", v1, False, WHITE),
            ("D", l2, True, LGREY), ("E", v2, False, WHITE)
        ]:
            c = ws[f"{col}{row}"]
            c.value = val
            c.font = font(bold=bold, color=ORANGE if bold else BLACK, size=9)
            c.fill = fill(bg)
            c.border = border()

    ws.row_dimensions[8].height = 6

    # ── TABLE HEADERS ─────────────────────────────────────────────────────────
    headers = ["ISBN", "TITLE", "GR", "LANGUAGE", "PUBLISHER", "UNIT PRICE", "QTY", "LINE TOTAL"]
    cols = ["A", "B", "C", "D", "E", "F", "G", "H"]
    ws.column_dimensions["H"].width = 16

    for col, hdr in zip(cols, headers):
        c = ws[f"{col}9"]
        c.value = hdr
        c.font = font(bold=True, color=WHITE, size=9)
        c.fill = fill(BLACK)
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border()
    ws.row_dimensions[9].height = 18

    # ── DATA ROWS ─────────────────────────────────────────────────────────────
    grand_total = 0
    for idx, item in enumerate(items):
        row = 10 + idx
        shade = LGREY if idx % 2 == 0 else WHITE
        line_total = item["price"] * item["qty"]
        grand_total += line_total
        ws.row_dimensions[row].height = 16

        data = [
            ("A", item["isbn"]),
            ("B", item["title"]),
            ("C", item["grade"]),
            ("D", item["language"]),
            ("E", item["publisher"]),
            ("F", item["price"]),
            ("G", item["qty"]),
            ("H", line_total),
        ]
        for col, val in data:
            c = ws[f"{col}{row}"]
            c.value = val
            c.font = font(size=9)
            c.fill = fill(shade)
            c.border = border()
            if col in ["F", "H"]:
                c.number_format = 'R#,##0.00'
            if col == "G":
                c.alignment = Alignment(horizontal="center")

    # ── GRAND TOTAL ───────────────────────────────────────────────────────────
    total_row = 10 + len(items)
    ws.merge_cells(f"A{total_row}:G{total_row}")
    tc = ws[f"A{total_row}"]
    tc.value = "GRAND TOTAL"
    tc.font = font(bold=True, color=WHITE, size=11)
    tc.fill = fill(BLACK)
    tc.alignment = Alignment(horizontal="right", vertical="center")
    tc.border = border()
    ws.row_dimensions[total_row].height = 22

    gt = ws[f"H{total_row}"]
    gt.value = grand_total
    gt.font = font(bold=True, color=WHITE, size=11)
    gt.fill = fill(ORANGE)
    gt.border = border()
    gt.number_format = 'R#,##0.00'

    # ── FOOTER ────────────────────────────────────────────────────────────────
    footer_row = total_row + 2
    ws.merge_cells(f"A{footer_row}:H{footer_row}")
    ft = ws[f"A{footer_row}"]
    ft.value = "Kalikeng Trading and Projects CC  |  Excellence in Service Delivery Since 2010"
    ft.font = font(size=8, color="555555")
    ft.alignment = Alignment(horizontal="center")

    filename = f"Quote_{ref_no}_{school.replace(' ','_')}.xlsx"
    wb.save(filename)
    return filename, grand_total

def main():
    print("\n" + "="*60)
    print("   KALIKENG TEXTBOOK & STATIONERY QUOTE BUILDER")
    print("="*60)

    school = input("\nEnter school/client name: ").strip()
    ref_no = input("Enter quotation number (e.g. KT-2026-001): ").strip()

    items = []
    print("\nSearch by ISBN or title. Type 'done' when finished.\n")

    while True:
        query = input("Search ISBN or title (or 'done'): ").strip()
        if query.lower() == "done":
            break
        if not query:
            continue

        results = search_books(query)
        if not results:
            print("  No results found. Try again.\n")
            continue

        print(f"\n  Found {len(results)} result(s):")
        for i, book in enumerate(results, 1):
            isbn_clean = str(book["isbn"]).replace(".0","")
            print(f"  [{i}] {isbn_clean} | {book['title'][:50]} | Gr{book['grade']} | R{book['price']} | {book['publisher']}")

        choice = input("\n  Select number (or Enter to skip): ").strip()
        if not choice:
            continue

        try:
            selected = results[int(choice) - 1]
            qty = input(f"  Quantity for '{selected['title'][:40]}': ").strip()
            qty = int(qty)
            if qty > 0:
                selected["qty"] = qty
                selected["isbn"] = str(selected["isbn"]).replace(".0","")
                items.append(selected)
                line = qty * selected["price"]
                print(f"  ✓ Added — Line total: R{line:,.2f}\n")
        except (ValueError, IndexError):
            print("  Invalid selection. Try again.\n")
            continue

    if not items:
        print("\nNo items added. Exiting.")
        return

    print(f"\nBuilding quote with {len(items)} items...")
    filename, total = build_quote(items, school, ref_no)
    print(f"\n{'='*60}")
    print(f"  QUOTE SAVED: {filename}")
    print(f"  GRAND TOTAL: R{total:,.2f}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()