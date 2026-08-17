from flask import Flask
from test_blueprints.auth import auth
from test_blueprints.api import api


app = Flask(__name__)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(api, url_prefix="/api")

@app.errorhandler(404)
def server_not_found(e):
    return "Server not found", 404

if __name__ == "__main__":
    app.run(debug=True)