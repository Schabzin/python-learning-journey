from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def search_books(query):
    conn = sqlite3.connect("books.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM books 
        WHERE isbn LIKE ? OR title LIKE ?
        ORDER BY title
        LIMIT 50
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()
    return [dict(row) for row in results]

@app.route("/")
def home():
    return render_template("search_engine.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form["query"].strip()
        if query:
            results = search_books(query)
    return render_template("search_engine.html", results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)