from flask import Flask, jsonify,request, render_template

app = Flask(__name__)

products = [
    {"id": 1, "name": "Milk", "price": 25.50},
    {"id": 2, "name": "Sugar", "price": 50.00},
    {"id": 3, "name": "Butter", "price": 35.00}
]

@app.route("/api/products", methods=["GET", "POST"])
def get_products():
    if request.method == "GET":
        return jsonify(products)
    if request.method == "POST":
        data = request.get_json()
        if not data or not data.get("name"):
            return jsonify({"error": "Name required"}), 400
        name = data["name"]
        price = data.get("price", 0)
        products.append({"id": len(products) + 1, "name": name, "price": price})
        return jsonify({"message": "Product created"}), 201
    
@app.route("/test_fetch")
def test_fetch():
    return render_template("test_fetch.html")

if __name__== "__main__":
    app.run(debug=True)

