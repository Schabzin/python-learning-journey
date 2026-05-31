from flask import Flask
from auth.routes import auth
from dashboard.routes import dashboard

app = Flask(__name__)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(dashboard, url_prefix="/dashboard")

if __name__ == "__main__":
    app.run(debug=True)