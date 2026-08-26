from flask import Flask, request, render_template, jsonify
import sqlite3

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

@app.route("/api/lookup")
def lookup_by_isbn():
    search_term = request.args.get("q", "").strip()
    conn = sqlite3.connect("textbooks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, price, isbn FROM books
        WHERE isbn = ? OR title LIKE ?
        LIMIT 1
    """, (search_term, f"%{search_term}%"))
    book = cursor.fetchone()
    conn.close()
    if book:
        return jsonify({"found": True, "title": book["title"], "price": book["price"], "isbn": book["isbn"]})
    return jsonify({"found": False})

@app.route("/quote")
def quote_builder():
    return render_template("quote_builder.html")



if __name__ == "__main__":
    app.run(debug=True)