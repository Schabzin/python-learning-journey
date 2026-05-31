from flask import Flask
from auth.routes import auth
from dashboard.routes import dashboard

app = Flask(__name__)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(dashboard, url_prefix="/dashboard")

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found, Separaka Taxi System", 404

@app.errorhandler(500)
def server_error(e):
    return "Server error, contact admin", 500

if __name__ == "__main__":
    app.run(debug=True)