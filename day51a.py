from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print("Form submitted:", request.form)
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()

        errors = []

        if not username:
            errors.append("Username is required")

        if len(username) < 3:
            errors.append("Username must be at least 3 characters")

        if not password:
            errors.append("Password is required")

        if len(password) < 6:
            errors.append("Password must be at least 6 characters")

        if "@" not in email:
            errors.append("Valid email is required")

        if errors:
            return jsonify({"errors": errors}), 400
        
        return jsonify({"message": "Registration successful"}), 201
    return render_template("register.html")
    
if __name__ == "__main__":
    app.run(debug=True)