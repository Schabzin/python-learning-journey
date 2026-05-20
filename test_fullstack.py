from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

orders = [
    {"id":1, "product": "Pen", "amount": 3.50 },
    {"id":2, "product": "Ruler", "amount": 2.20},
    {"id":3, "product": "Stapler", "amount": 75.90}

]

@app.route("/api/orders",methods=["GET","POST"])
def get_orders():
    if request.method == "GET":
        return jsonify(orders)
    if request.method == "POST":
        data = request.get_json()
        if not data or not data.get("product"):
            return jsonify({"error": "Product required"}), 400
        product = data["product"]
        amount = data.get("amount", 0)
        orders.append({"id": len(orders) + 1, "product": product, "amount": amount})
        return jsonify({"message": "Orders created"}), 201
    
@app.route("/api/orders/<int:id>", methods= ["DELETE"])
def delete_orders(id):
    order = next((o for o in orders if o["id"] == id), None)
    if not order:
        return jsonify({ "error": "Order not found"}), 404
    orders.remove(order)
    return jsonify({"message": "Deleted"}), 200
    
@app.route("/test_fullstack")
def test_fullstack():
    return render_template("test_fullstack.html")

if __name__ == "__main__":
    app.run(debug=True)
    
