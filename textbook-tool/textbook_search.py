from flask import Flask, request, render_template, jsonify
import sqlite3
import io
import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from flask import send_file
from fuzzywuzzy import fuzz

app = Flask(__name__)

@app.route("/search")
def search_books():
    query = request.args.get("q", "", type=str)
    conn = sqlite3.connect("textbooks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if query:
        cursor.execute("""
            SELECT title, publisher, price FROM books
            WHERE title LIKE ?
            ORDER BY title
        """, (f"%{query}%",))
    else:
        cursor.execute("SELECT title, publisher, price FROM books ORDER BY title LIMIT 20")

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return render_template("book_search.html", results=results, query=query)


@app.route("/quote")
def quote_builder():
    return render_template("quote_builder.html")


@app.route("/api/lookup")
def lookup_by_isbn():
    search_term = request.args.get("q", "").strip()
    conn = sqlite3.connect("textbooks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT title, price, isbn, grade FROM books WHERE isbn = ?", (search_term,))
    book = cursor.fetchone()

    if not book:
        cursor.execute("SELECT title, price, isbn, grade FROM books")
        all_books = cursor.fetchall()
        best_match = None
        best_score = 0
        for candidate in all_books:
            score = fuzz.ratio(search_term.lower(), candidate["title"].lower())
            if score > best_score:
                best_score = score
                best_match = candidate
        if best_score >= 85:
            book = best_match

    conn.close()
    if book:
        return jsonify({"found": True, "title": book["title"], "price": book["price"], "isbn": book["isbn"], "grade": book["grade"]})
    return jsonify({"found": False})

@app.route("/api/generate-quote", methods=["POST"])
def generate_quote():
    data = request.get_json()
    items = data.get("items", [])
    school = data.get("school", "")
    quote_number = data.get("quote_number", "")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    NAVY = colors.HexColor("#1B3A5C")
    ORANGE = colors.HexColor("#C85A00")
    BLACK = colors.black
    WHITE = colors.white

    white_style = ParagraphStyle("white", parent=styles["Normal"], textColor=WHITE, alignment=1)
    gold_style = ParagraphStyle("gold", parent=styles["Normal"], textColor=ORANGE, alignment=1)
    company_style = ParagraphStyle("company", parent=styles["Normal"], textColor=WHITE, fontSize=14, alignment=1, spaceAfter=4)
    cell_style = ParagraphStyle("cell", parent=styles["Normal"], fontSize=8, leading=10)
    grand_label_style = ParagraphStyle("grand_label", parent=styles["Normal"], textColor=WHITE, alignment=2, fontSize=8)

    header_lines = [
        [Paragraph("KALIKENG TRADING AND PROJECTS CC", company_style)],
        [Paragraph("Reg No: 2010/007041/23 | VAT No: 4340257320 | Tel: 073 223 9762 | Kalikeng@gmail.com", gold_style)],
        [Paragraph("2438 Total Street, Zone 13, Sebokeng, 1982", white_style)],
        [Paragraph("B-BBEE Level 1 | 100% Black Owned | 135% Procurement Recognition", white_style)],
    ]
    header_box = Table(header_lines, colWidths=[468])
    header_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLACK),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, -1), (-1, -1), 3, ORANGE),
    ]))

    gold_para = ParagraphStyle("gold_left", parent=styles["Normal"], textColor=ORANGE)
    right_align_style = ParagraphStyle("right_gold", parent=styles["Normal"], textColor=ORANGE, alignment=2)
    story = [
        header_box,
        Spacer(1, 16),
        Paragraph(f"Quotation No: {quote_number}", gold_para),
        Paragraph(f"Date: {datetime.date.today().isoformat()}", right_align_style),
        Paragraph(f"School/Client: {school}", gold_para),
        Paragraph("Prepared by: Sechaba Mofokeng", right_align_style),
        Spacer(1, 16)
    ]

    grades = {}
    for item in items:
        grades.setdefault(item["grade"], []).append(item)

    rows = [["#", "ISBN", "TITLE", "UNIT PRICE", "QTY", "LINE TOTAL"]]
    item_num = 1
    grand_total = 0
    
    for grade, books in grades.items():
        grade_total = 0
        for book in books:
            line_total = float(book["price"]) * int(book["qty"])
            grade_total += line_total
            
            title_text = book["title"]
            if f"(GRADE {grade})" not in title_text:
                title_text = f"{title_text} (GRADE {grade})"

            rows.append([str(item_num), book["isbn"], Paragraph(title_text, cell_style),
                         f"R {book['price']}", str(book["qty"]), f"R {line_total:,.2f}"])
            item_num += 1
        rows.append(["", "", "", "", "TOTAL", f"R {grade_total:,.2f}"])
        grand_total += grade_total

    rows.append([Paragraph("GRAND TOTAL (VAT Incl.)", grand_label_style),"", "", "", "", f"R {grand_total:,.2f}"])
    grand_total_row_index = len(rows) - 1 

    col_widths = [20, 80, 185, 60, 35, 88]
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), BLACK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("SPAN", (0, grand_total_row_index), (4, grand_total_row_index)),
        ("BACKGROUND", (0, grand_total_row_index), (4, grand_total_row_index), BLACK),
        ("TEXTCOLOR", (0, grand_total_row_index), (4, grand_total_row_index), WHITE),
        ("BACKGROUND", (5, grand_total_row_index), (5, grand_total_row_index), ORANGE),
        ("TEXTCOLOR", (5, grand_total_row_index), (5, grand_total_row_index), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"quotation_{quote_number}.pdf", mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)