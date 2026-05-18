from flask import Flask, request, render_template

app = Flask(__name__)

orders = [
    {"id":1, "product": "Pen", "amount": 3.50 },
    {"id":2, "product": "Ruler", "amount": 2.20},
    {"id":3, "product": "Stapler", "amount": 75.90}

]

@app.route("/api/orders",method=["GET"])
def orders:
    request method="GET"
    
