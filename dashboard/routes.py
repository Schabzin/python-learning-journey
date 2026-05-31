from flask import Blueprint

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/home")
def home():
    return "Dashboard home"