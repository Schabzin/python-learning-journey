from collections import defaultdict
import time
from functools import wraps
from flask import Flask, request, jsonify


app = Flask(__name__)

request_counts = defaultdict(list)

def rate_limit(max_requests=3, window=10):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = time.time()
            request_counts[ip] = [t for t in request_counts[ip] if now - t < window]
            if len(request_counts[ip]) >= max_requests:
                return jsonify({"error": "Too many requests"}), 429
            request_counts[ip].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/test")
@rate_limit(max_requests=3, window=10)
def test():
    return jsonify({"message": "Request successful"}), 200


if __name__ == "__main__":
    app.run(debug=True)