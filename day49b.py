from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import RequestEntityTooLarge
import os
import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return "File too large - maximum size is 2MB", 413

def get_upload_path(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        folder = "uploads/documents"
    elif ext in {"png", "jpg", "jpeg"}:
        folder = "uploads/images"
    else:
        folder = "uploads/other"
    os.makedirs(folder, exist_ok=True)
    return folder

def unique_filename(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{filename}"

    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "size": os.path.getsize(filepath),
        "path": filepath
    }), 200
    
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["document"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = unique_filename(filename)
            folder = get_upload_path(filename)
            filepath = os.path.join(folder, filename)
            file.save(filepath)
            return jsonify({
                "message": "File uploaded successfully",
                "filename": filename,
                "size": os.path.getsize(filepath),
                "path": filepath
            }), 200
        return "Invalid file type", 400
    return render_template("uploads.html")

if __name__ == "__main__":
    app.run(debug=True)