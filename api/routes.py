from flask import Blueprint

api = Blueprint("api", __name__)

@api.route("/data")
def data():
    return "API data"