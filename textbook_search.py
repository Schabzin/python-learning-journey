from flask import Flask, request, render_template, jsonify
import sqlite3
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
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

@app.route("/api/generate-quote", methods=["POST"])
def generate_quote():
    data = request.get_json()
    items = data.get("items", [])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Kalikeng Trading and Projects CC", styles["Title"]), Spacer(1, 16)]

    rows = [["ISBN", "Title", "Price", "Qty", "Total"]]
    grand_total = 0
    for item in items:
        line_total = float(item["price"]) * int(item["qty"])
        grand_total += line_total
        rows.append([item["isbn"], item["title"], f"R{item['price']}", item["qty"], f"R{line_total:.2f}"])
    rows.append(["", "", "", "Grand Total:", f"R{grand_total:.2f}"])

    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1, 0), colors.HexColor("#1B3A5C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer,as_attachment=True, download_name="quotation.pdf", mimetype="application/pdf")

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


if __name__ == "__main__":
    app.run(debug=True)