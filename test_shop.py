from flask import Flask, url_for, redirect, request, render_template,flash
import sqlite3
import re

app = Flask (__name__)
app.secret_key = "testshop2026"

def get_items():
    conn = sqlite3.connect("test_shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall ()
    conn.close()
    return products

@app.route("/products")
def products():
    products = get_items()
    return render_template("products.html", products=products)

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]

        conn = sqlite3.connect("test_shop.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name,price,stock)
            VALUES (?,?,?)
        """,(name, price, stock))
        conn.commit()
        conn.close()

        flash("Product added successfully!", "success")
        return redirect(url_for("products"))
    
    return render_template("add_product.html")

@app.route("/edit_product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    conn= sqlite3.connect("test_shop.db")
    conn.row_factory= sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]
        cursor.execute("""
            UPDATE products SET name=?, price=?, stock=?
            WHERE id=?)
        """, (name, price, stock,id))
        conn.commit()
        conn.close()
        cursor.execute("SELECT * FROM products WHERE id=?, (id)")
        return redirect(url_for("products"))
        product = cursor.fetchone()
        conn.close()
        return render_template("edit_product.htm", product=product)
    
@app.route("/delete_product/<int:id>", methods=["GET"])
def delete_product(id):
    conn = sqlite3.connect("test_shop_db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash(f"Product deleted successfully!")
    return redirect(url_for("products"))

if __name__ == "__main__":
    app.run(debug=True)


