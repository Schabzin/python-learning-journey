from flask import Blueprint, jsonify

api = Blueprint("api", __name__)

@api.route("/data")
def data():
    return jsonify({"status": "ok", "data": "API working"})
