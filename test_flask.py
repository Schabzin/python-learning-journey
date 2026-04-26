from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    company= "Kalikeng Trading and Projects CC"
    year= 2026
    tagline = "Your trusted supply and transport partner"
    return render_template("test_index.html", company=company, year=year, tagline=tagline)

@app.route("/employee/<name>")
def employee(name):
    return f"Welcome employee: {name}"


@app.route("/about")
def about():
    return render_template("test_about.html")

if __name__ == "__main__":
   app.run(debug=True)

