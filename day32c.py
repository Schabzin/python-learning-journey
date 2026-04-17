from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", company="Kalikeng Trading")

@app.route("/about")
def about():
    return render_template("about.html", city="Sebokeng", year=2010)

@app.route("/clients")
def clients():
    clients = [
        ["Sechaba", 7500, "Paid"],
        ["Nomvula", 5000, "Unpaid"],
        ["Rorisang", 3000, "Paid"]
    ]
    return render_template("clients.html", clients=clients)
              
if __name__ == "__main__":
    app.run(debug=True)
 