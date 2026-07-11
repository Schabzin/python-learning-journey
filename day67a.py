from functools import wraps
from flask import Flask, url_for, redirect, jsonify, session

def my_decorator(f):
    def wrapper(*args, **kwargs):
        print("Before the function runs")
        result = f(*args, **kwargs)
        print("After the function runs")
        return result
    return wrapper

@my_decorator
def greet(name):
    print(f"Hello, {name}")

greet("Chahane")

def log_action(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated
    
def log_action(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "owner":
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated
