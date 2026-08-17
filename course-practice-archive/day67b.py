from functools import wraps
from flask import Flask, session, redirect, url_for, jsonify

app = Flask(__name__)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            if session.get("role") != role:
                return jsonify({"error": f"{role} access required"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
              
@role_required("owner")
def dashboard():
    pass


@role_required("marshall")
def log_trip():
    pass


if __name__ == "__main__":
    app.run(debug=True)
        