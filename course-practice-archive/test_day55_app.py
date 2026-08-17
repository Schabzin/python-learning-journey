import logging
from test_config import ProductionConfig
from flask import Flask, jsonify

app = Flask(__name__)
app.config.from_object(ProductionConfig)

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s"
)

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}")
    return jsonify({"error": "Server Error"}), 500

@app.errorhandler(403)
def unauthorized(e):
    return jsonify({"error": "Unauthorized"}), 403

@app.route("/crash")
def crash():
    raise Exception("Test crash")

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
                         
if __name__ == "__main__":
    app.run(debug=False)


