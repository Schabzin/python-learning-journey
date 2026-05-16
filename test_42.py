from flask import Flask, request, jsonify, render_template


app = Flask(__name__)

suppliers = [
    {"id": 1, "name": "Oxford", "amount": 5000},
    {"id": 2, "name": "Maskew Miller", "amount": 8000},
    {"id": 3, "name": "Vivlia", "amount": 3500}
]


@app.route("/api/suppliers", methods=["GET", "POST"])
def get_all_suppliers():
    if request.method == "GET":
        return jsonify(suppliers)
    if request.method == "POST":
        data = request.get_json()
        if not data or not data.get("name"):
            return jsonify({"error": "Name is required"}), 400
        name = data["name"]
        amount = data.get("amount", 0)  
        suppliers.append({"id": len(suppliers) + 1, "name": name, "amount": amount})
        return jsonify({"message": "Supplier created", "name": name}), 201
    
@app.route("/api/suppliers/<int:id>", methods=["DELETE"])
def delete_suppliers(id):
    supplier = next((s for s in suppliers if s["id"] == id), None)
    if not supplier:
        return jsonify({"error": "Supplier not found"}), 404
    suppliers.remove(supplier)
    return jsonify({"message": "Deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
    

