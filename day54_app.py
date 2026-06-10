
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify({"items": []}), 200

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    name = data.get("name") if data else None
    if not name:
        return jsonify({"error": "Name is required"}), 400
    return jsonify({"message": "Item created"}), 201

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    return jsonify({"error": "Client not found"}), 404



if __name__ == "__main__":
    app.run(debug=True)
                        